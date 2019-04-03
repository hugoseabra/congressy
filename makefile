

up:
	mkdir -p /tmp/bkp;
	sudo cp bin/env/extension_installer.sh /tmp/bkp/;
	docker-compose -f bin/env/docker-compose_dev.yml up -d;
	-pkill -f "celery worker";
	celery --app=mailer --app=gatheros_subscription worker --loglevel=INFO --detach;
	docker logs -f cgsy-postgres;


down:
	-pkill -f "celery worker";
	docker-compose -f bin/env/docker-compose_dev.yml down;


celery_down:
	-pkill -f "celery worker";

celery_up:
	celery --app=mailer --app=gatheros_subscription worker --loglevel=INFO;


logs:
	docker-compose -f bin/env/docker-compose_dev.yml logs -f


pgadmin:
	docker network inspect pg &>/dev/null || docker network create pg;
	[ ! "$(docker ps -a | grep pgadmin)" ] &>/dev/null; docker start pgadmin || docker run -d -p 5050:5050 --name pgadmin  -v ~/pgadmin:/pgadmin --network=pg  thajeztah/pgadmin4;
	[ ! "$(docker ps -a | grep cgsy-postgres)" ] &>/dev/null || docker network connect pg cgsy-postgres;
