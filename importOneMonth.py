#!/usr/bin/python3
import argparse
import hourly

parser = argparse.ArgumentParser(description='Import just one month of hourly data into the SQLITE3 database.')
parser.add_argument('--city', default='ottawa')
parser.add_argument('--year', type=int, required=True)
parser.add_argument('--month', type=int, required=True)
args = parser.parse_args()

data = hourly.loadEnvCan(args.city, args.year, args.month)
hourly.saveSql(data, args.city)
