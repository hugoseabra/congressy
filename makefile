DOCKER_COMPOSE_ENV=bin/env/docker-compose_dev.yml

CELERY_SERVICES=-A attendance -A mailer -A gatheros_subscription -A buzzlead worker

.PHONY: export_settings
up: export_settings
	@make broker_create
	docker-compose -f $(DOCKER_COMPOSE_ENV) up -d --remove-orphans;
	@make logs


.PHONY: down
down: broker_kill
	docker-compose -f $(DOCKER_COMPOSE_ENV) down --remove-orphans;


.PHONY: stop
stop: broker_kill
	docker-compose -f $(DOCKER_COMPOSE_ENV) stop;


.PHONY: broker_kill
broker_kill:
	ps x --no-header -o pid,cmd | awk '!/awk/&&/celery/{print $$1}' | xargs -r kill;


.PHONY: broker_create
broker_create: broker_kill
	celery -E $(CELERY_SERVICES) --loglevel=INFO --pidfile="/tmp/celery.pid" --detach;


.PHONY: broker_debug
broker_debug: broker_kill
	celery -E $(CELERY_SERVICES) --loglevel=INFO;


.PHONY: services
services:
	docker-compose -f $(DOCKER_COMPOSE_ENV) ps


.PHONY: logs
logs:
	docker-compose -f $(DOCKER_COMPOSE_ENV) logs -f

.PHONY: update_db
update_db:
	mkdir -p /tmp/bkp;
	sudo cp bin/env/extension_installer.sh /tmp/bkp/;
	python manage.py makemigrations; python manage.py migrate
	python manage.py loaddata 000_site_dev

.PHONY: restart_ngrok
restart_ngrok:
	docker-compose -f $(DOCKER_COMPOSE_ENV) stop ngrok
	docker-compose -f $(DOCKER_COMPOSE_ENV) rm ngrok
	docker-compose -f $(DOCKER_COMPOSE_ENV) up -d
	docker-compose -f $(DOCKER_COMPOSE_ENV) logs -f ngrok


.PHONY: export_settings
export_settings:
	export DJANGO_SETTINGS_MODULE=project.manage.settings.dev

.PHONY: clean
clean:
	sudo rm -rf /tmp/exporter
