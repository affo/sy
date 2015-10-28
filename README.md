# Sy - ([or "eye" in Albanian](https://translate.google.it/#en/sq/eye))

A monitoring agent for Docker containers.  
Sy pushes information retrieved from sensors both to RabbitMQ queues and a Redis storage --- depending on the sensor's type.

## Install
For a quickstart, use the `Makefile` that uses [Docker Compose](https://docs.docker.com/compose/):

 - `make`: runs Redis and RabbitMQ containers publishing on ports 9000 and 5672 respectively;
 - `make clean`: removes `-f` the composed containers.

Tu use Sy, `source syrc` and launch `sy-agent -d`. You can use `sy` CLI to interact with the daemon.

## Running tests

```
$ python -m unittest discover -v
```
