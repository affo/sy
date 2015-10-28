all: backends

backends: clean
	docker-compose up -d

clean:
	docker rm -f sy_rabbit_1; true
	docker rm -f sy_redis_1; true
