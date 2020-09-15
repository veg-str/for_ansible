#!/usr/bin/python

import argparse
import csv
import datetime
import json
import logging
import os
import subprocess
import sys
import threading
import re
from datetime import date
from time import sleep


parser = argparse.ArgumentParser(description='Stats fetcher')
parser.add_argument('-c', '--config', type=str, help='Path to configuration file')
parser.add_argument('-d', '--day', type=str, help='The date from which to fetch statistics')
parser.add_argument('-l', '--list', type=str, help='List of MSISDNs')

PLSTATLIST = '../deps/plstatlist'

if os.path.exists(PLSTATLIST):
    plstatlistbin = PLSTATLIST


def get_msisdn_list(fname):
    # Get list of MSISDNs from file
    msisdns = []
    with open(fname, 'r') as f:
        for line in f:
            if re.search("\d{11}", line):
                msisdns.append(re.search("\d{11}", line).group(0))

    # Split list into small parts (500 MSISND per list)
    msisdn_full = []
    while len(msisdns) != 0:
        tmp_list = []
        i = 0
        while i < 500 and len(msisdns) > 0:
            tmp_list.append(msisdns.pop(0))
            i = i + 1
        msisdn_full.append(tmp_list)
    return msisdn_full


def valid_date_format(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        return False
    return True


def first_day():
    return date.fromordinal(date.toordinal(date.today()) - 99)


def last_day():
    return date.fromordinal(date.toordinal(date.today()) - 70)


class StatsFetcher(threading.Thread):
    def __init__(self, host, user, password, date_start, date_end, path, fields, output_folder, msisdn):
        threading.Thread.__init__(self, name='StatsFetcher')
        self.host = host
        self.user = user
        self.password = password
        self.date_start = date_start
        self.date_end = date_end
        self.path = path
        self.fields = fields
        self.output_folder = output_folder
        self.first_row_read = False
        self.msisdn = msisdn

    def run(self):
        self.plstatlist()

        logging.info("Exiting...")

    def plstatlist(self):
        params = [self.host, self.date_start, self.date_end, self.path, '--csv', ','.join(self.fields), '-u', self.user, '-p', self.password]

        out = self.fetch(params)

        t = datetime.datetime.now()

        filename = '%s%s_%s_%s.csv' % (self.output_folder, t.strftime('%Y-%m-%d-%s'), self.host, self.msisdn)

        logging.debug("Generating report: %s..." % filename)

        with open(filename, 'w') as csvfile:
            w = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
            for row in csv.reader(out):
                if not self.first_row_read:
                    row[0] = "msisdn"
                    row[1] = "service"

                    self.first_row_read = True
                else:
                    if row[3] == "0":
                        continue
                    try:
                        row[1] = self.path.split (self.path.split("?")[1])[1].split("/")[1]
                    except Exception as e:
                        pass
                w.writerow(row)
            csvfile.close()

        logging.info("Generated report: %s" % filename)

    def fetch(self, args):
        cmd_args = [plstatlistbin] + [str(x) for x in args]
        logging.debug("CMD='%s'", ' '.join(cmd_args))
        cmd = subprocess.Popen(cmd_args, stdout=subprocess.PIPE)
        res = cmd.stdout
        cmd.stdout.close()
        return res


if __name__ == '__main__':

    # Parse arguments
    args = parser.parse_args()
    if not args.config:
        sys.exit("Missing configuration file.")

    # Parse configuration
    try:
        config = json.loads(file(args.config).read())
    except Exception as e:
        sys.exit('Failed to parse config')

    lvl = logging.DEBUG if 'debug' == str(config.get('log_level')).lower() else logging.INFO
    logging.basicConfig(filename=config['log'], level=lvl, format='%(asctime)s (%(levelname)s): %(message)s', stream=sys.stdout)

    logging.info("Starting...")

    # If the day from which to fetch stats is defined, we use that. Otherwise we fetch stats from last day
    if args.day:
        if not valid_date_format(args.day):
            logging.error("Incorrect data format, should be YYYY-MM-DD. Exiting...")
        start = "%s %s" % (args.day, "00:00")
        end = "%s %s" % (args.day, "23:59")
    else:
        start = "%s %s" % (first_day(), "00:00")
        end = "%s %s" % (last_day(), "23:59")

    # Get list of MSISDNs
    if args.list:
        msisdn_all = get_msisdn_list(args.list)
    else:
        msisdn_all = list(re.search("\d{11}", config["path"]).group(0))

        # Iterate through MSISDN list if exist. Otherwise take argument from config
    for msisdn_list in msisdn_all:
        for msisdn in msisdn_list:
            curr_path = re.sub("\d{11}", msisdn, config["path"])

            # Create one thread for each host
            threads = []
            for host in config['hosts']:
                threads.append(StatsFetcher(host, config['user'], config['password'], start, end, curr_path,
                                        config["fields"], config['output_folder'], msisdn))

            # Start threads
            for t in threads:
                t.start()
        sleep(60)

