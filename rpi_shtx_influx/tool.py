"""
Command-line tool to endlessly produce metrics
"""

import os
from time import sleep
from rpi_shtx_influx.temperature import TemperatureReader
from socket import gethostname
import argparse

def main():
    parser = argparse.ArgumentParser('RPi+SHTx->InfluxDB logger')
    parser.add_argument('--bucket', default=os.getenv('INFLUX_BUCKET'), help='InfluxDB bucket name')
    parser.add_argument('--org', default=os.getenv('INFLUX_ORG'), help='InfluxDB Org name')
    parser.add_argument('--token', default=os.getenv('INFLUX_TOKEN'), help='InfluxDB token with access to the given bucket')
    parser.add_argument('--url', default=os.getenv("INFLUX_URL"), help='URL to InfluxDB')
    parser.add_argument('--hostname', default=gethostname(), help='Hostname of this machine to report to Influx')
    parser.add_argument('--read-interval', type=int, default=10, help='Time in seconds between data readings')
    args = parser.parse_args()

    temp = TemperatureReader(args.bucket, args.org, args.token, args.url, args.hostname)
    while True:
        temp.fetch_and_write_metrics()
        sleep(args.read_interval)
