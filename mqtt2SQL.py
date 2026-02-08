# MQTT Connector to SQL
# VICTOR CASTHELAIN - 2026
# version 1.0.1

# IMPORTS
import paho.mqtt.client as mqtt
import mysql.connector
import json
import os

# =========================
# ENV VARIABLES
# =========================

MQTT_BROKER=os.getenv("MQTT_BROKER") # CONST BROKER IP ADDR
MQTT_TOPIC=os.getenv("MQTT_TOPIC") # CONST TOPIC TO SUB
MQTT_PORT=os.getenv("MQTT_PORT") # CONST BROKER PORT
SQL_SERVER=os.getenv("SQL_SERVER") # CONST SQL IP ADDR
SQL_PORT=os.getenv("SQL_PORT") # CONST SQL PORT
SQL_DB=os.getenv("SQL_DB") # CONST SQL DATABASE FOR CHECK
SQL_USER=os.getenv("SQL_USER") # CONST SQL USER
SQL_PASSWORD=os.getenv("SQL_PASSWORD") # CONST SQL PASSWORD
SQL_SECRET=os.getenv("SQL_SECRET") # CONST PATH TO SECRET FILE (WIP)

# =========================
# MQTT CALLBACKS
# =========================
'''
ON_CONNECT is a callback function that is call when it connect to the MQTT BROKER
This is where it will subscribed to the topics we want to received and send to the database.
'''
def on_connect(client, userdata, flags, rc):
    print("MQTT connected with code", rc)
    client.subscribe(MQTT_TOPIC)

'''
ON_MESSAGE is the callback function when we received a message from a subscribed topic
When it received a message, it first open a connection to the db. then if the connection is good.
It open a cursor (to execute the insert), process the information to put it in a SQL insert request
'''
def on_message(client, userdata, msg):
    
    mydb = mysql.connector.connect(
        host=SQL_SERVER,
        user=SQL_USER,
        password=SQL_PASSWORD,
        database=SQL_DB
    )
    cursor = mydb.cursor()
    
    payload = json.loads(msg.payload.decode())
    print(f"MQTT message: {payload}")
    
    if payload["database"]== SQL_DB:
        request = create_request(payload["table"],payload["data"])
        print(request)
        cursor.execute(request)
        mydb.commit()
        cursor.close()
        mydb.close()
    else:
        print("Error : database name not matching")
    

# =========================
# MQTT MESSAGE TO SQL
# =========================
'''
format type of a MQTT message to convert :

{
  "database":"mydb",
  "table":"Temperature",
  "data":{
    "temperature_1":"24",
    "temperature_2":"25"
  }
}

into :

INSERT INTO Temperature (temperature_1,temperature_2) VALUES (24,25)

'''
def create_request(table,data_array):
    request = f"INSERT INTO {table}"
    columns = ""
    values = ""
    for k, v in data_array.items():
        if columns != "" and values != "":
            columns = columns + "," + str(k)
            values = values + "," +str(v)
        else :
            columns = str(k)
            values = str(v)
            
    request = request + " ("+columns+")"+ " VALUES ("+values+")"
    return request
    

# =========================
# MQTT CLIENT
# =========================
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()
