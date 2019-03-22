

up:
	docker-compose -f bin/env/docker-compose_dev.yml up -d; docker logs -f cgsy-postgres;


down:
	docker-compose -f bin/env/docker-compose_dev.yml down

pgadmin:
	docker network inspect pg &>/dev/null || docker network create pg;
	[ ! "$(docker ps -a | grep pgadmin)" ] &>/dev/null; docker start pgadmin || docker run -d -p 5050:5050 --name pgadmin  -v ~/pgadmin:/pgadmin --network=pg  thajeztah/pgadmin4;
	[ ! "$(docker ps -a | grep cgsy-postgres)" ] &>/dev/null || docker network connect pg cgsy-postgres;