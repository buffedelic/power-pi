#!/usr/bin/env python

from __future__ import division
from signal import pause
#import time
import time
import sys
import schedule
import argparse
from influxdb import InfluxDBClient
import ow #keeping us from python3 :(

DATABASE = 'power'


l_cnt_1 = 0 #Total 1D00FD0C0000009B counter A
l_cnt_2 = 0 #Heater 1D00FD0C0000009B
l_cnt_3 = 0 #FTX 1D00FD0C0000009B
l_out_file = "/home/pi/power-pi/power-pi.txt"
l_poll_minutes = 1
l_verbosemode = True
l_first_run = True

milliseconds = lambda: int(time.time() * 1000)
l_millis = milliseconds()

def insert_row(json_body):
    client = InfluxDBClient(host='localhost', port=8086, username='mqtt', password='mqtt')
    client.switch_database(DATABASE)
    try:
        print("Writing to db")
        client.write_points(json_body)
    except:
        pass
    client.close()

def do_purge():
    #client = InfluxDBClient(host='localhost', port=8086)
    #client.switch_database(DATABASE)
    
    # open(l_out_file, 'w')
    exit(0)

def logmsg(msg):
    msg_text = "{} {}".format(time.strftime("%d/%m/%Y %H:%M:%S"), msg)
    print(msg_text)
    with open(l_out_file,'a') as f:
        f.write("{}\n".format(msg_text))
        
def handle_time_event():
    global l_first_run

    if not l_first_run:
        
        global l_cnt_1
        global l_cnt_2
        global l_cnt_3
        global l_millis
        l_cnt_1_last = l_cnt_1
        l_cnt_2_last = l_cnt_2
        l_cnt_3_last = l_cnt_3
        l_millis_last = l_millis

        ow.init('localhost:4304')
        l_cnt_1 = int(ow.Sensor( '/1D6CEC0C00000094').counter_A)
        l_cnt_2 = int(ow.Sensor( '/1D00FD0C0000009B').counter_A)
        l_cnt_3 = int(ow.Sensor( '/1D00FD0C0000009B').counter_B)

        
        l_millis = milliseconds()
        interval_millis = l_millis - l_millis_last

        # P(w) = (3600 / T(s)) / ppwh
        # watt = (3600000 / ((interval_millis / interval_count)) / 1) or 0.8
        try:
            watt_total = ( 3600000 / (interval_millis / (l_cnt_1 - l_cnt_1_last))) / 1
        except ZeroDivisionError:
            watt_total = 0 
        try:
            watt_heater = ( 3600000 / (interval_millis / (l_cnt_2 - l_cnt_2_last))) / 0.8
        except ZeroDivisionError:
            watt_heater = 0 
        try:
            watt_ftx = ( 3600000 / (interval_millis / (l_cnt_3 - l_cnt_3_last))) / 1
        except ZeroDivisionError:
            watt_ftx = 0 

        ow.finish()
        logmsg("Pulses total={}, Pulses heater={}  Pulses FTX={}".format((l_cnt_1 - l_cnt_1_last), (l_cnt_2 - l_cnt_2_last), (l_cnt_3 - l_cnt_3_last)))
        json_body = [
        {
            "measurement": "power_total",
            "tags": {
                "dev_id": "1D6CEC0C00000094",
                "instance": "counter.A"
            },
            "fields": {
                "watt": round(watt_total,2)
            }
        },
        {
            "measurement": "power_heater",
            "tags": {
                "dev_id": "1D00FD0C0000009B",
                "instance": "counter.A"
            },
            "fields": {
                "watt": round(watt_heater,2)
            }
        },
        {
            "measurement": "power_ftx",
            "tags": {
                "dev_id": "1D00FD0C0000009B",
                "instance": "counter.A"
            },
            "fields": {
                "watt": round(watt_ftx,2)
            }
        }
        ]
        #print(json_body)
        insert_row(json_body)
    else:
        l_first_run = False
        ow.init('localhost:4304')
        l_cnt_1 = int(ow.Sensor( '/1D6CEC0C00000094').counter_A)
        l_cnt_2 = int(ow.Sensor( '/1D00FD0C0000009B').counter_A)
        l_cnt_3 = int(ow.Sensor( '/1D00FD0C0000009B').counter_B)
        ow.finish()

def main():
    global l_verbosemode
    parser = argparse.ArgumentParser(description='Power monitor.')
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
    parser.add_argument("-p", "--purge", help="purge file and database", action="store_true")
    args = parser.parse_args()

    if (args.purge):
        do_purge()

    l_verbosemode = args.verbose

    handle_time_event()
    schedule.every(l_poll_minutes).minutes.do(handle_time_event)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
