# MQTT2SQL
SQL Connector from MQTT Broker

## Description

Repository of an example of application that can be embedded in an [Softing Industrial edgeNode](https://industrial.softing.com/products/gateways/gateways-for-access-of-controller-data/edgenode-portainer.html)
This is not an industrial proof application.
Please keep in mind that this code is provided for functionnality demo purposes only.
Use at your own risk.

## Installation

### Dockerfile

Clone this repo and compress it to .tar.gz. You can then upload it to your docker environnement or throught Portainer.

### Dockerhub
```
docker container run -e MY_ENVIRONEMENT="VALUE" erabitrix/mqtt2mysql
```
```
ENVIRONNEMENT VARIABLES :
MQTT_BROKER="127.0.0.1"
MQTT_TOPIC="localhost/sql"
MQTT_PORT="1883"
SQL_SERVER="127.0.0.1"
SQL_PORT="3306"
SQL_DB=""
SQL_USER=""
SQL_PASSWORD=""
```