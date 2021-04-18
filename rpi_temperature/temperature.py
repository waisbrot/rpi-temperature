#!/usr/bin/env python3

import logging
import adafruit_si7021
from socket import gethostname
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
import os
from time import sleep
import board

log = logging.getLogger('main')

sensor = None
influx = None
bucket = os.getenv('INFLUX_BUCKET')
org = os.getenv('INFLUX_ORG')
token = os.getenv('INFLUX_TOKEN')
url = os.getenv("INFLUX_URL")
hostname = gethostname()
influx_init_count = 0
sensor_init_count = 0
last_temperature = 0
last_humidity = 0
same_reading = 0
read_interval_s = 10
max_same_reads = 60

while True:
        if not sensor:
                log.debug("Initializing temp sensor")
                sensor_init_count += 1
                sensor = adafruit_si7021.SI7021(board.I2C())
        if not influx:
                log.debug("Initializing Influx client")
                influx_init_count += 1
                client = InfluxDBClient(url=url, token=token, org=org)
                influx = client.write_api(write_options=SYNCHRONOUS)
        temperature = sensor.temperature
        humidity = sensor.relative_humidity
        metrics = [
                f'temperature,host={hostname} degrees_c={temperature}',
                f'humidity,host={hostname} humidity_pct={humidity}',
                f'sensor_initialized,host={hostname} count={sensor_init_count}',
                f'influx_initialized,host={hostname}, count={influx_init_count}',
        ]
        if last_temperature == temperature and last_humidity == humidity:
                same_reading += 1
        else:
                same_reading = 0
        if same_reading > max_same_reads:
                log.error(f'Same reading from the sensors {same_reading} in a row. Resetting sensor.')
                sensor = None

        log.debug(f"Going to write to influx: {metrics}")
        try:
                influx.write(bucket=bucket, record=metrics)
        except:
                log.error("Failed to write to Influx. Will try to reconnect next time.")
                influx = None
        sleep(read_interval_s)
