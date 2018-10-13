###############################################################################
# CUIDADO!
# Esta script é gerenciado pelo CI. Não altere ou mude sem saber o que está
# fazendo.
###############################################################################
# CI-STEP: verifica última versão publicada
#
# Busca a última com versão (padrão semver) mais alta e compara com a versão
# do build. Se diferente e maior, persistir em um arquivo com valor "1".
###############################################################################

import os
import subprocess

import semver
from clint.textui import colored, puts


def shell_do(cmd, **kwargs):
    process = subprocess.Popen(cmd.format(**kwargs), shell=True,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE,
                               universal_newlines=True)
    out, err = process.communicate()

    if err:
        puts(colored.red(err))

    return out


BASE = os.path.dirname(__file__)

REPO_LINK = '871800672816.dkr.ecr.us-east-1.amazonaws.com'
REPO_NAME = 'cgsy'

LATEST_IMAGE = shell_do(
    'docker exec -i awsecr last-image {}'.format(REPO_NAME)
)

CURRENT_VERSION = str(LATEST_IMAGE).replace(
    'Repository: {}\n'.format(REPO_NAME),
    ''
)
CURRENT_VERSION = str(CURRENT_VERSION).replace(
    '{}/{}:'.format(REPO_LINK, REPO_NAME),
    ''
)

NEXT_VERSION_FILE = os.path.join(BASE, '..', '..', '..', 'version')
NEXT_VERSION = shell_do('cat {}'.format(NEXT_VERSION_FILE))

NEXT_VERSION = str(NEXT_VERSION).rstrip('\r\n')
CURRENT_VERSION = CURRENT_VERSION.rstrip('\r\n')

print("CURRENT VERSION: {}".format(CURRENT_VERSION))
print("VERSION TO DEPLOY: {}".format(NEXT_VERSION))

higher_version = semver.compare(CURRENT_VERSION, NEXT_VERSION) == -1

if higher_version is False:
    raise Exception('Deploy encerrado por não haver nova versão.')

tagged_version_file = os.path.join(BASE, 'tagged_version')

with open(tagged_version_file, 'w+') as f:
    print("Registrando versão a ser liberada '{}' em '{}'.".format(
        NEXT_VERSION,
        tagged_version_file
    ))

    # 1 significa que os processos continuarão.
    f.write('1')
    f.close()

previous_version_file = os.path.join(BASE, 'previous_version')

with open(previous_version_file, 'w+') as f:
    f.write(CURRENT_VERSION)
    f.close()
    print("Registrando versão atual '{}' em '{}'.".format(
        CURRENT_VERSION,
        previous_version_file
    ))
