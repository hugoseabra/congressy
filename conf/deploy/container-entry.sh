#!/usr/bin/env bash

echo "########################################################################"
echo "PROCESSANDO ENTRY"
echo "########################################################################"

echo " > Configurando WSGI"
# configures wsgi
python /configure-wsgi.py

echo " > Configurando NGINX"
# configures nginx
python /configure-nginx.py

echo " > Configurando SYNC"
# configures sync process workflow
python /configure-sync.py

chmod 777 /s3bucket.sh /in-sync.sh

# Verifies if bucket exists. If not, creates it.
/s3bucket.sh

echo ;
echo "========================================================================"
echo " > Puxando arquivos existentes no S3"
echo ;
# Runs in-sync: configuration state has priority of outsite if bucket exists
/in-sync.sh
echo ;
echo "========================================================================"
echo ;

echo " > Configurando CRONTAB"
# Inject schedule configuration
echo "" >> /crontab.txt
crontab /crontab.txt

echo " > Configurando DB"
# Configures database app credentials
python /configure-db.py

echo " > Configurando RODAPÉ"
# Configures footer
python /configure-footer.py

echo " > Coletando arquivos estáticos"
# Collect all static data
python manage.py collectstatic --noinput --verbosity 0

echo ;
echo "========================================================================"
echo " > Executando migrate"
echo ;
python manage.py migrate
echo ;
echo "========================================================================"
echo ;

echo " > Iniciando SUPERVISOR"
echo ;
echo "########################################################################"
supervisord -n
