# Encoding: UTF-8
"""
Uso:
    fab [target] [action ...]

Ex:
fab --list
fab -H landare setup_server:target='test',document_root='/var/www/testes'
fab -H landare deploy:target='test',document_root='/var/www/testes'
fab -H landare deploy:target='test',document_root='/var/www/testes',reinstalldb=True
fab -H landare disable:target='test',document_root='/var/www/testes'

Requisitos:
Fabric==1.13.2

"""
import ConfigParser
import os
from StringIO import StringIO
from datetime import datetime

from django.utils.crypto import get_random_string
from fabric.api import *
from fabric.contrib import files
from jinja2 import Template

##############################################################################
# Configurações do projeto
##############################################################################

env.base_name = 'gatheros.com'  # Nome principal do projeto nas configurações
env.python = '/usr/bin/python3.4'  # Path do python a ser usado

SETTINGS_CONF = """
\"\"\"
------------------------------------------------------------------------------
 !!CUIDADO!!
 Este arquivo é criado por um template, alterações feitas diretamente, podem
 ser perdidas na configuração de uma nova versão do script
------------------------------------------------------------------------------
\"\"\"
from .settings import *

SECRET_KEY = '{{secret_key}}'
DATABASES = {
    'default': {
        'ENGINE':'django.db.backends.postgresql_psycopg2',
        'NAME': '{{dbname}}',
        'USER': '{{dbuser}}',
        'PASSWORD': '{{dbpass}}',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
"""

FIXTURES = [
    '001_user',
    '005_user',
    '006_person',
    '007_organization',
    '008_member',
    '009_place',
    '010_event',
    '011_info',
    '012_invitation',
    '001_default_field',
    '002_default_field_option',
    '003_form',
    '004_field',
    '005_field_option',
    '006_lot',
    '007_subscription',
    '008_answer'
]  # Dados de teste usados na execução do 'deploy' com 'reinstalldb=True'


##############################################################################
# Tarefas executaveis
##############################################################################
@task
def deploy(target='prod', document_root='/var/www/', reinstalldb=False):
    """
    Atualiza uma instância para a versão mais nova

    :param target:
        prefixo a ser colocado no nome do projeto para indicar sua
        finalidade 'prod': produção, 'test': teste etc
    :param document_root:
        Diretório onde será colocado o projeto
    :param reinstalldb:
        Usado em instancias de teste para recarregar os dados de teste,
        para evistar problemas um backup é gerado antes de qualquer
        alteração ser executada
    """
    defaults(target=target, document_root=document_root)

    with cd(env.deploy_dir), prefix('source venv/bin/activate'):
        run('git pull origin master')
        install_requirements()
        run('supervisorctl stop %s' % ' '.join(get_supervisor_services()))

        if reinstalldb == 'True' or reinstalldb is True:
            reinstall_database()
        else:
            migrate()

        config_supervisor()
        config_nginx()


@task
def disable(target='prod', document_root='/var/www/'):
    """
    Desabilita uma instância

    Para preservar os dados do banco e arquivos da instância, tanto o banco
    quando o diretório de deploy são renomeados

    :param target:
        prefixo a ser colocado no nome do projeto para indicar sua
        finalidade 'prod': produção, 'test': teste etc
    :param document_root:
        Diretório onde será colocado o projeto
    """
    defaults(target=target, document_root=document_root)
    pre = 'disabled_%s' % datetime.now().strftime('%Y%m%d%H%M')

    # Renomeia o banco
    if check_dbname(False):
        sql = 'ALTER DATABASE {0} RENAME TO {1}_{0};'.format(env.dbname, pre)
        sudo('psql -c "%s"' % sql, user='postgres')

    # Renomeia o usuário do banco
    if check_dbuser(False):
        sql = 'ALTER USER {0} RENAME TO {1}_{0};'.format(env.dbname, pre)
        sudo('psql -c "%s"' % sql, user='postgres')

    # Renomeia o diretório de deploy
    if files.exists(env.deploy_dir):
        parent_dir = os.path.abspath(os.path.join(env.deploy_dir, '..'))
        new_dir = os.path.join(parent_dir, '%s_%s' % (pre, env.full_name))
        run('mv %s %s' % (env.deploy_dir, new_dir))

    # Apagando conf do nginx
    if files.exists(env.nginx_file):
        run('rm -f %s' % env.nginx_file)
        run('/etc/init.d/nginx configtest')
        run('/etc/init.d/nginx reload')

    # Apagando conf do supervisor
    if files.exists(env.supervisor_file):
        run('rm -f %s' % env.supervisor_file)
        run('supervisorctl reread')
        run('supervisorctl reload')


@task
def setup_server(target='prod', document_root='/var/www/'):
    """
    Configura o servidor e faz o primeiro deploy

    :param target:
        prefixo a ser colocado no nome do projeto para indicar sua
        finalidade 'prod': produção, 'test': teste etc
    :param document_root:
        Diretório onde será colocado o projeto
    """
    defaults(target=target, document_root=document_root)

    require('deploy_dir')
    require('git_url')
    require('python')

    # Instala os pacotes de sistema requeridos
    install_packages()

    # Verificando instalações anteriores
    try:
        check_dbname()
        check_dbuser()
        check_project()
    except Exception as e:
        abort(
            """
    %s. 
    Para limpar antes execute:
        fab -H %s setup_server:target='%s',document_root='%s'
            """ % (
                str(e),
                env.host_string,
                target,
                document_root
            ))

    # Clone do repositório
    config_ssh_key()
    run('git clone %s %s' % (env.git_url, env.deploy_dir))

    # Cria virtualenv
    run('pip install virtualenv')
    with cd(env.deploy_dir):
        run('virtualenv -p %s venv' % env.python)

    # Configuração do servidor pypi privado
    mkdir('~/.pip/')
    content = StringIO("""
[global]
extra-index-url = http://kanu:kanu@pypi.kanusoftware.com/simple/

[install]
trusted-host=pypi.kanusoftware.com
    """)
    put(local_path=content, remote_path='~/.pip/pip.conf')

    # Instalando dependências
    install_requirements()

    # Criando usuário do banco
    create_dbuser()

    # Criando banco novo
    create_dbinstance()

    # Criando senha do banco e secret key para o settings
    require('dbpass')
    kwargs = {
        'dbpass': env.dbpass,
        'dbuser': env.dbuser,
        'dbname': env.dbname,
        'secret_key': generate_password(),
        'target': env.target
    }
    template = Template(SETTINGS_CONF.decode('utf-8'))
    content = template.render(kwargs).encode('utf-8')
    put(local_path=StringIO(content), remote_path=env.settings_file)

    # Criando diretório paga guardar os uploads
    mkdir(get_settings_value('MEDIA_ROOT'))

    # Migrando banco e coletando assets
    migrate()
    collectstatic()

    # Configurar supervisor
    config_supervisor()

    # Configurar ngix
    config_nginx()

    # Check django
    check()


@task
def restore(target='prod', document_root='/var/www/'):
    """
    Restaura uma instância desabilitada

    :param target:
        prefixo a ser colocado no nome do projeto para indicar sua
        finalidade 'prod': produção, 'test': teste etc
    :param document_root:
        Diretório onde será colocado o projeto
    """
    abort('Não terminado')
    # Listar as opções que combinam com o target
    # Mostrar menu com a escolha para o usuário
    # Proceder o rename do diretorio, banco e usuário
    # Redefinir a senha do usuário conforma a configuração
    # Recriar as configurações do supervisor e nginx


##############################################################################
# Funções auxiliares
##############################################################################

def install_packages():
    """
    Instala os pacotes de sistema configurados
    """
    require('local_dir')
    config_file = os.path.join(env.local_dir, 'requirements_os.conf')
    config = ConfigParser.SafeConfigParser()
    config.read(config_file)

    run(u"apt-get update")
    for role in config.sections():
        run(u"apt-get install -y %s" % config.get(role, 'packages'))


def config_ssh_key():
    """
    Configura as chaves ssh
    """
    put(os.path.join(env.conf_root, 'id_rsa'), '~/.ssh/', mode='600')
    put(os.path.join(env.conf_root, 'id_rsa.pub'), '~/.ssh/', mode='600')


def get_settings_value(name):
    with cd(env.deploy_dir), prefix('source venv/bin/activate'):
        return run(
            'echo "from django.conf import settings; '
            'print(settings.%s)" | '
            'python manage.py shell' % name)


def defaults(target='prod', document_root='/var/www/'):
    """
    Configura os valores padrão

    :param target:
        prefixo a ser colocado no nome do projeto para indicar sua
        finalidade 'prod': produção, 'test': teste etc
    :param document_root:
        Diretório onde será colocado o projeto
    """
    require('base_name')

    env.service_daemon = 'upstart'
    env.use_ssh_config = True
    env.target = target
    env.full_name = '%s.%s' % (target, env.base_name)
    normalized_name = env.full_name.replace('.', '_')
    env.dbname = normalized_name
    env.dbuser = normalized_name
    env.deploy_dir = os.path.join(document_root, env.full_name)
    env.local_dir = os.path.dirname(__file__)
    env.conf_root = os.path.join(env.local_dir, 'conf')
    env.settings_module = 'project.settings.%s' % env.target
    env.nginx_file = '/etc/nginx/sites-enabled/%s' % env.full_name
    env.supervisor_file = '/etc/supervisor/conf.d/%s.conf' % env.full_name
    env.settings_file = os.path.join(env.deploy_dir, 'project/settings/',
                                     '%s.py' % env.target)

    with lcd(env.local_dir):
        env.git_url = local('git config --get remote.origin.url', True)


def mkdir(path, user='www-data', group='www-data'):
    """
    Cria diretórios e muda dono
    :param path:
    :param user:
    :param group:
    """
    run('mkdir -p ' + path)
    run('chown {0}:{1} -R {2}'.format(user, group, path))


def install_requirements():
    """
    Atualiza pacotes do projeto
    """
    require('hosts')
    require('deploy_dir')

    with cd(env.deploy_dir), prefix('. venv/bin/activate'):
        run('pip install -r requirements.txt')


def get_next_port(start=9500):
    """
    Acha a proxima porta não utilizada do sistema

    :param start: valor inicial da procura
    :return: int
    """

    def next_port(start):
        num = start
        while True:
            yield num
            num += 1

    for port in next_port(start):
        content = run('netstat -anp |grep :%s || echo ""' % port)
        if not content.strip():
            return port


def config_nginx():
    """
    Configura o projeto no nginx
    """
    require('deploy_dir')
    require('full_name')
    require('gunicorn_port')

    files.upload_template('conf/nginx', env.nginx_file, context=env,
                          use_jinja=True, backup=False)

    run('/etc/init.d/nginx configtest')
    run('/etc/init.d/nginx reload')


def config_supervisor():
    """
    Configura o projeto no supervisord
    """
    require('deploy_dir')
    require('full_name')

    env.gunicorn_port = get_next_port(start=9500)

    files.upload_template('conf/supervisor.conf', env.supervisor_file,
                          context=env, use_jinja=True, backup=False)

    run('supervisorctl reread')
    run('supervisorctl reload')


def management_cmd(cmd):
    """
    Executa um comando de gerenciamento do django

    :param cmd:
    """
    require('hosts')
    require('deploy_dir')

    with cd(env.deploy_dir), prefix('source venv/bin/activate'):
        run("python manage.py %s --settings %s" % (cmd, env.settings_module))


def check():
    """ Perform Django's deploy systemchecks. """
    management_cmd('check --deploy')


def migrate():
    """
    Executa migração do banco
    """
    management_cmd("migrate --noinput")


def collectstatic():
    """
    Coleta arquivos staticos
    """
    management_cmd('collectstatic --noinput')


def generate_password(length=50):
    """
    Similar to Django's charset but avoids $ to avoid accidential shell
    variable expansion

    :param length: int
    :return: str
    """
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#%^&*(-_=+)'
    return get_random_string(length, chars)


def check_dbname(raise_error=True):
    """
    Verifica se o banco existe

    :return: bool
    """
    require('dbname')

    sql = "SELECT 1 FROM pg_database WHERE datname='%s'" % env.dbname

    if sudo('psql -tAc "%s"' % sql, user='postgres') == '1':
        if raise_error:
            raise Exception('O banco de dados "%s" existe' % env.dbname)
        return True
    return False


def check_dbuser(raise_error=True):
    """
    Verifica se o usuário de banco existe

    :return: bool
    """
    require('dbuser')

    sql = "SELECT 1 FROM pg_roles WHERE rolname='%s'" % env.dbuser

    if sudo('psql -tAc "%s"' % sql, user='postgres') == '1':
        if raise_error:
            raise Exception('O usuário de banco "%s" existe' % env.dbuser)
        return True
    return False


def check_project(raise_error=True):
    """
    Verifica se o projeto existe

    :return: bool
    """
    all_exceptions = []

    # Nginx
    if files.exists(env.nginx_file):
        all_exceptions.append('O arquivo de configuração "%s" já existe' %
                              env.nginx_file)

    # Supervisor
    if files.exists(env.supervisor_file):
        all_exceptions.append('O arquivo de configuração "%s" já existe' %
                              env.supervisor_file)

    # Diretório do projeto
    if files.exists(env.deploy_dir):
        all_exceptions.append('O diretório "%s" já existe' % env.deploy_dir)

    if all_exceptions and raise_error:
        raise Exception('. '.join(all_exceptions))

    return len(all_exceptions) > 0


def get_supervisor_services():
    """
    Extraindo os nomes dos serviços supervisord relacionados

    :return: list[str]
    """
    require('full_name')

    services = []
    for line in run('supervisorctl status').strip().split("\n"):
        service_name = line.split(' ')[0]
        if env.full_name in service_name:
            services.append(service_name)

    return services


def create_dbuser():
    """
    Criar usuário do banco
    """
    require('dbuser')
    require('dbname')

    # Criando usuário do banco
    env.dbpass = generate_password()
    sql = "CREATE USER {0} WITH password '{1}';".format(
        env.dbuser, env.dbpass)
    sudo('psql -c "%s"' % sql, user='postgres')


def create_dbinstance():
    """
    Criar banco
    """
    require('dbuser')
    require('dbname')

    sql = """
    CREATE DATABASE {0}
      WITH OWNER = {1}
        ENCODING = 'UTF8'
        TABLESPACE = pg_default
        LC_COLLATE = 'pt_BR.UTF-8'
        LC_CTYPE = 'pt_BR.UTF-8'
        CONNECTION LIMIT = -1;
    """.format(env.dbname, env.dbuser)
    sudo('psql -c "%s"' % sql, user='postgres')


def reinstall_database():
    """
    Reinstala o banco de dados e executa os fixtures, para evistar problemas
    um backup é gerado antes de qualquer alteração ser executada

    :param fixtures: lista de fixtures
    """

    # Se o banco existe, precisa fazer um backup antes de excluir
    if check_dbname(raise_error=False):
        # Verifica se existe o diretório para salvar o backup
        if not files.exists('/backup/'):
            abort('Não foi possível criar um backup do banco, '
                  'o diretório "/backup/" não existe.')

        # Executa o backup
        bkp_name = '/backup/reinstalldb_{0}_{1}.sql'.format(
            datetime.now().strftime('%Y%m%d%H%M'),
            env.dbname
        )
        command = 'pg_dump --format=c --file="{0}" {1}'.format(
            bkp_name, env.dbname)
        sudo(command, user='postgres')

        # Informa o usuário
        warn('Um backup foi criado em: {0}'.format(bkp_name))

        # Removendo o banco antigo
        sudo('psql -c "DROP DATABASE %s;"' % env.dbname, user='postgres')

    # Criando banco novo
    create_dbinstance()

    # Migrando banco
    migrate()

    # Instalando fixtures informados
    for item in FIXTURES:
        management_cmd("loaddata %s" % item)
