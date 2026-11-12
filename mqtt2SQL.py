#!/usr/bin/env python3

"""
MQTT Connector to SQL
Author: Victor Casthelain
Version: 1.0.3
"""

import json
import logging
import os
import re

import mysql.connector
import paho.mqtt.client as mqtt
from mysql.connector import Error


# ==========================================================
# LOGGING
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# ==========================================================
# ENVIRONMENT VARIABLES
# ==========================================================

MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "localhost/sql")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))

SQL_SERVER = os.getenv("SQL_SERVER", "127.0.0.1")
SQL_PORT = int(os.getenv("SQL_PORT", "3306"))
SQL_DB = os.getenv("SQL_DB", "my_database")
SQL_USER = os.getenv("SQL_USER", "root")

SQL_SECRET = os.getenv(
    "SQL_SECRET",
    "/run/secrets/sql_password"
)

SQL_PASSWORD = os.getenv("SQL_PASSWORD")


# ==========================================================
# SECRET MANAGEMENT
# ==========================================================

if not SQL_PASSWORD:
    try:
        with open(SQL_SECRET, "r", encoding="utf-8") as secret:
            SQL_PASSWORD = secret.read().strip()
            logger.info("Password loaded from Docker Secret")
    except FileNotFoundError:
        logger.error(
            "No SQL_PASSWORD variable and no secret file found"
        )
        raise SystemExit(1)


# ==========================================================
# CONFIG DISPLAY
# ==========================================================

logger.info("Starting MQTT SQL Connector")

logger.info(
    "MQTT => broker=%s port=%s topic=%s",
    MQTT_BROKER,
    MQTT_PORT,
    MQTT_TOPIC
)

logger.info(
    "SQL => server=%s port=%s database=%s user=%s",
    SQL_SERVER,
    SQL_PORT,
    SQL_DB,
    SQL_USER
)


# ==========================================================
# VALIDATION
# ==========================================================

VALID_IDENTIFIER_REGEX = re.compile(r"^[a-zA-Z0-9_]+$")


def validate_identifier(name: str) -> bool:
    """
    Prevent SQL injection via table/column names.
    """
    return bool(VALID_IDENTIFIER_REGEX.fullmatch(name))


# ==========================================================
# DATABASE
# ==========================================================

def get_db_connection():
    """
    Create a MySQL connection.
    """

    return mysql.connector.connect(
        host=SQL_SERVER,
        port=SQL_PORT,
        user=SQL_USER,
        password=SQL_PASSWORD,
        database=SQL_DB,
        autocommit=False
    )


# ==========================================================
# SQL REQUEST CREATION
# ==========================================================

def build_insert_query(table: str, data: dict):
    """
    Creates a parameterized INSERT statement.

    Example:
        INSERT INTO Temperature
        (temperature_1, temperature_2)
        VALUES (%s, %s)
    """

    if not validate_identifier(table):
        raise ValueError(f"Invalid table name: {table}")

    if not data:
        raise ValueError("Empty data payload")

    for column in data.keys():
        if not validate_identifier(column):
            raise ValueError(
                f"Invalid column name: {column}"
            )

    columns = ", ".join(data.keys())
    placeholders = ", ".join(
        ["%s"] * len(data)
    )

    query = (
        f"INSERT INTO {table} "
        f"({columns}) "
        f"VALUES ({placeholders})"
    )

    values = list(data.values())

    return query, values


# ==========================================================
# MQTT CALLBACKS
# ==========================================================

def on_connect(client, userdata, flags, reason_code, properties=None):

    if reason_code == 0:
        logger.info(
            "Connected to MQTT broker %s",
            MQTT_BROKER
        )

        client.subscribe(MQTT_TOPIC)

        logger.info(
            "Subscribed to topic %s",
            MQTT_TOPIC
        )

    else:
        logger.error(
            "MQTT connection failed (%s)",
            reason_code
        )


def on_message(client, userdata, msg):

    logger.info(
        "Message received on topic %s",
        msg.topic
    )

    try:

        payload = json.loads(
            msg.payload.decode("utf-8")
        )

        logger.debug(payload)

        required_fields = [
            "database",
            "table",
            "data"
        ]

        for field in required_fields:
            if field not in payload:
                raise ValueError(
                    f"Missing field: {field}"
                )

        if payload["database"] != SQL_DB:

            logger.warning(
                "Rejected request for database '%s'",
                payload["database"]
            )

            return

        query, values = build_insert_query(
            table=payload["table"],
            data=payload["data"]
        )

        logger.info(
            "Executing INSERT on table %s",
            payload["table"]
        )

        connection = None
        cursor = None

        try:

            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute(query, values)

            connection.commit()

            logger.info(
                "Record inserted successfully"
            )

        finally:

            if cursor:
                cursor.close()

            if connection:
                connection.close()

    except json.JSONDecodeError:

        logger.error(
            "Invalid JSON payload received"
        )

    except Error as db_error:

        logger.error(
            "Database error: %s",
            db_error
        )

    except Exception as error:

        logger.error(
            "Processing error: %s",
            error
        )


# ==========================================================
# MQTT CLIENT
# ==========================================================

def main():

    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2
    )

    client.on_connect = on_connect
    client.on_message = on_message

    logger.info(
        "Connecting to MQTT broker..."
    )

    client.connect(
        MQTT_BROKER,
        MQTT_PORT,
        60
    )

    client.loop_forever()


if __name__ == "__main__":
    main()