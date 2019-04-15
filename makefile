

up:
	ps x --no-header -o pid,cmd | awk '!/awk/&&/celery/{print $$1}' | xargs -r kill;
	celery -A attendance -A mailer -A gatheros_subscription worker --loglevel=INFO --detach;
	mkdir -p /tmp/bkp;
	sudo cp bin/env/extension_installer.sh /tmp/bkp/;
	docker-compose -f bin/env/docker-compose_dev.yml up -d --remove-orphans;
	docker-compose -f bin/env/docker-compose_dev.yml logs -f;


down:
	ps x --no-header -o pid,cmd | awk '!/awk/&&/celery/{print $$1}' | xargs -r kill;
	docker-compose -f bin/env/docker-compose_dev.yml down --remove-orphans; docker volume prune -f;


clean:
	sudo rm -rf /tmp/exporter


debug_broker:
	ps x --no-header -o pid,cmd | awk '!/awk/&&/celery/{print $$1}' | xargs -r kill;
	celery -A attendance -A mailer -A gatheros_subscription worker --loglevel=INFO;


logs:
	docker-compose -f bin/env/docker-compose_dev.yml logs -f


pgadmin:
	docker network inspect pg &>/dev/null || docker network create pg;
	[ ! "$$(docker ps -a | grep pgadmin)" ] &>/dev/null; docker start pgadmin || docker run -d -p 5050:5050 --name pgadmin  -v ~/pgadmin:/pgadmin --network=pg  thajeztah/pgadmin4;
	[ ! "$$(docker ps -a | grep cgsy-postgres)" ] &>/dev/null || docker network connect pg cgsy-postgres;
