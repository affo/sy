# Sy - ([or "eye" in Albanian](https://translate.google.it/#en/sq/eye))

A monitoring agent for Docker containers.  

Sy needs to be installed directly on the Docker host and to be associated with a [Docker Compose](https://docs.docker.com/compose/) stack.  
Sy pushes information retrieved from sensors both to RabbitMQ queues and a Redis storage --- depending on the sensor's type.

### Running tests

```
$ python -m unittest discover -v
```
