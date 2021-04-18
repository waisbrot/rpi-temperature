"""
Command-line tool to endlessly produce metrics
"""

import os
from time import sleep
from rpi_shtx_influx.temperature import TemperatureReader
from socket import gethostname
import argparse
import logging

def main():
    parser = argparse.ArgumentParser(description='RPi+SHTx->InfluxDB logger')
    parser.add_argument('--bucket', default=os.getenv('INFLUX_BUCKET'), help='InfluxDB bucket name')
    parser.add_argument('--org', default=os.getenv('INFLUX_ORG'), help='InfluxDB Org name')
    parser.add_argument('--token', default=os.getenv('INFLUX_TOKEN'), help='InfluxDB token with access to the given bucket')
    parser.add_argument('--url', default=os.getenv("INFLUX_URL"), help='URL to InfluxDB')
    parser.add_argument('--hostname', default=gethostname(), help='Hostname of this machine to report to Influx')
    parser.add_argument('--read-interval', type=int, default=10, help='Time in seconds between data readings')
    parser.add_argument('--sensor-address', default=0x40, type=int, help='i2c address of the sensor. i2cdetect may help')
    parser.add_argument('-v', action='count', default=0, help='Logging verbosity. One for info, two for debug')
    args = parser.parse_args()

    loglevel = logging.WARNING
    if args.v > 0:
        loglevel = logging.INFO
    if args.v > 1:
        loglevel = logging.DEBUG
    logging.basicConfig(level=loglevel)
    
    temp = TemperatureReader(args.bucket, args.org, args.token, args.url, args.hostname, sensor_addr=args.sensor_address)
    while True:
        temp.fetch_and_write_metrics()
        sleep(args.read_interval)
