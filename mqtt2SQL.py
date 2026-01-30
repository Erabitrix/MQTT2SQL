# MQTT Connector to SQL
# VICTOR CASTHELAIN - 2026
# version 1.0.0

# IMPORTS
import paho.mqtt.client as mqtt
import mysql.connector
import json


# =========================
# SQL CONNECTION INFOS
# =========================

#IMPORTANT TO DETERMINE IF SENDING DATA TO THE CORRECT DB
database="mydb" 

# =========================
# MQTT CALLBACKS
# =========================
'''
ON_CONNECT is a callback function that is call when it connect to the MQTT BROKER
This is where it will subscribed to the topics we want to received and send to the database.
'''
def on_connect(client, userdata, flags, rc):
    print("MQTT connected with code", rc)
    client.subscribe("localhost/sql")

'''
ON_MESSAGE is the callback function when we received a message from a subscribed topic
When it received a message, it first open a connection to the db. then if the connection is good.
It open a cursor (to execute the insert), process the information to put it in a SQL insert request
'''
def on_message(client, userdata, msg):
    
    mydb = mysql.connector.connect(
        host="172.19.0.2",
        user="root",
        password="rootpassword",
        database="mydb"
    )
    cursor = mydb.cursor()
    
    payload = json.loads(msg.payload.decode())
    print(f"MQTT message: {payload}")
    
    if payload["database"]== database:
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

client.connect("192.168.0.10", 1883, 60)
client.loop_forever()
