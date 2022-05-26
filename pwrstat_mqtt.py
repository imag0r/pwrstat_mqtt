#!/usr/bin/env python3

import os
import subprocess
from paho.mqtt import client as mqtt_client

mqqt_broker = os.environ['PWRSTAT_MQTT_BROKER']
mqqt_port = int(os.environ['PWRSTAT_MQTT_PORT'])
mqqt_client_id = os.environ['PWRSTAT_MQTT_CLIENT']
mqqt_username = os.environ['PWRSTAT_MQTT_USER']
mqqt_password = os.environ['PWRSTAT_MQTT_PASSWORD']
mqqt_topic = os.environ['PWRSTAT_MQTT_TOPIC']

def connect_mqtt() -> mqtt_client:
    client = mqtt_client.Client(mqqt_client_id)
    client.username_pw_set(mqqt_username, mqqt_password)
    client.connect(mqqt_broker, mqqt_port)
    return client

def get_ups_status():
    output = subprocess.check_output(("/usr/sbin/pwrstat", "-status"), shell=False)
    output = output.decode().split('\n')
    
    data = {}
    for line in output[10:-2]:
        name = line[:29].strip('.').strip()
        value = line[31:].strip()
        data[name] = value

    status = {}
    status["state"] = data["State"].split()[0]
    status["supply"] = data["Power Supply by"]
    status["voltage_in"] = data["Utility Voltage"].split()[0]
    status["voltage_out"] = data["Output Voltage"].split()[0]
    status["capacity_left"] = data["Battery Capacity"].split()[0]
    status["time_left"] = data["Remaining Runtime"].split()[0]
    status["load_watts"] = data["Load"].split()[0]
    status["load_percent"] = data["Load"].split()[1].split('(')[1]
    return status

def publish_status(topic_base, status):
    client = connect_mqtt();
    for key, value in status.items():
        client.publish(topic_base + "/" + key, value)

if __name__ == '__main__':
    status = get_ups_status()
    publish_status(mqqt_topic, status)
