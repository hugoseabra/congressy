
up: update_db
	@make broker_create
	docker-compose -f bin/env/docker-compose_dev.yml up -d --remove-orphans;
	@make logs


down: broker_kill
	docker-compose -f bin/env/docker-compose_dev.yml down --remove-orphans;


stop: broker_kill
	docker-compose -f bin/env/docker-compose_dev.yml stop;


broker_kill:
	ps x --no-header -o pid,cmd | awk '!/awk/&&/celery/{print $$1}' | xargs -r kill;


broker_create: broker_kill
	celery -E -A attendance -A mailer -A gatheros_subscription -A buzzlead worker --loglevel=INFO --detach;


broker_debug: broker_kill
	celery -E -A attendance -A mailer -A gatheros_subscription -A buzzlead worker --loglevel=INFO;


services:
	docker-compose -f bin/env/docker-compose_dev.yml ps


logs:
	docker-compose -f bin/env/docker-compose_dev.yml logs -f


update_db:
	mkdir -p /tmp/bkp;
	sudo cp bin/env/extension_installer.sh /tmp/bkp/;
	python manage.py makemigrations; python manage.py migrate


restart_ngrok:
	docker-compose -f bin/env/docker-compose_dev.yml stop ngrok
	docker-compose -f bin/env/docker-compose_dev.yml rm ngrok
	docker-compose -f bin/env/docker-compose_dev.yml up -d
	docker-compose -f bin/env/docker-compose_dev.yml logs -f ngrok


clean:
	sudo rm -rf /tmp/exporter
