#!/usr/bin/python

'''The script runs Live Tail and process the output to post every event to
Datadog's Events Dashboard and a data-point to custom metric loggly.livetail.dd_integ.count_404
every minute. The command this script runs is equivalent to "./livetail -m 404"
'''

#Dependent Python libs: datadog and sh, use pip to install those

from datadog import initialize, api
import time
import sys
import re
import sh
import os

def postEvent(line):
    title = "Loggly's LiveTail found a 404 on one of the web servers"
    text = line
    tags = ['Loggly LiveTail']
    api.Event.create(title=title, text=text, tags=tags)

'''main'''

TAILCLIENT_BIN_DIR="/home/ubuntu/tailclient-1.0.1/bin"

#Replace following creds with actual values
options = {
    'api_key': 'DATADOG_API_KEY',
    'app_key': 'DATADOG_APP_KEY'
}

initialize(**options)

os.chdir(TAILCLIENT_BIN_DIR)
cmd=sh.Command("./livetail")
LatestPosixTime = time.time()
CurrentPosixTime=LatestPosixTime
ctr=0
for line in cmd("-m","404",_iter=True): 
    if not re.match("Loggly-LiveTail:",line): continue
    postEvent(line)
    ctr+=1
    LatestPosixTime = time.time()
    if (LatestPosixTime-CurrentPosixTime)>60:
        api.Metric.send(metric='loggly.livetail.dd_integ.count_404', points=(LatestPosixTime,ctr))
        CurrentPosixTime=LatestPosixTime
        ctr=0
api.Metric.send(metric='loggly.livetail.dd_integ.count_404', points=(LatestPosixTime,ctr))
