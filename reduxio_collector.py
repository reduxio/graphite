#!/usr/bin/python
'''
Reduxio graphite collector

Version Number:       0.1

Change History
0.1   CREATION/RELEASE NOTE 03/19/2018
- script creation

Description:
This script collects array and per volume space and IO stats
from Reduxio storage. It is itended to run as a cron
job based on preferred schedule.
Setting the variable to_graphite to False will print the metrics
to stdout



Example:
reduxio_collector.py
'''

import sys
import requests
import graphyte
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)



# Configurable Parameters
metric_root = 'storage.reduxio'
graphite_server_address = 'localhost'
graphite_server_port = '2003'
array_url = "172.17.46.216"
array_name = "mango"
api_token = "fa743d41-d95c-43e2-945f-6583ff86993c"
# If set to False the metrics go to stdout
# If set to True the metrics go to graphite
to_graphite = True
performance_metrics  = ['io_read', 'io_write', 'io_total', 'throughput_read','throughput_write', 'throughput_total', 'latency_read','latency_write', 'latency_total']



def get_data(url, api_token):
    '''Str, Dict -> Json
    Providing the full API URL and required headers it will
    return the output of the get method in json format.

    >>> get_data('https://hx550.com/api/statistics/top_vols?unit=SECONDS&comparison_field=IO', {'Accept': 'application/json', 'X-Auth-Token': '2ca68c4e-9bee-4bed-860c-3c8e8b52c1b0'})
    ...
    '''

    headers = {'Accept': 'application/json', 'X-Auth-Token': api_token, 'X-TIMESTAMP-UTC': 'true', 'X-PRETTY-JSON': 'false'}
    try:
        get_json = requests.get(url, headers=headers, verify=False, timeout=200).json()
        return(get_json)
    except requests.exceptions.ConnectionError:
        if to_graphite:
            sys.exit(0)
        else:
            print("ERROR - Connection timeout of 1 minute and 30 secs")
            sys.exit(3)



def volume_stats(array_name, array_url, api_token):
    '''(str, str, str) -> none
    collects per volume level IO stats and send them
    to the forwarder function.

    >>> volume_stats('reduxio_prod', 'reduxio_prod.com', '2cb67c4s-6bee-2bed-210c-3d7e8b32c1b1')
    '''

    volume_details = 'https://{}/api/volumes'.format(array_url)
    # First i need to get the volume name and id and then run
    # the volume statistics API call for each volume id
    get_json = get_data(volume_details, api_token)
    if 'message' in get_json:
        pass
    else:
        for volume in get_json:
            volume_name = volume['name']
            volume_id = volume['id']
            volume_stats = 'https://{}/api/volumes/{}/performance?unit=SECONDS&limit=1'.format(array_url, volume_id)
            get_json_stats = get_data(volume_stats, api_token)
            for stats in get_json_stats:
                for key in performance_metrics:
                    metric = '{}.volume_stats.{}.{}'.format(array_name, volume_name, key)
                    if 'throughput' in key:
                        metric_value = stats[key]['size_in_bytes']
                    else:
                        metric_value = stats[key]
                    send_to(metric, metric_value)


def array_stats(array_name, array_url, api_token):
    '''(str, str, str) -> none
    Collects array wide IO stats and send them
    to the forwarder function.

    >>> array_stats('reduxio_prod', 'reduxio_prod.com', '2cb67c4s-6bee-2bed-210c-3d7e8b32c1b1')
    '''

    volume_stats = 'https://{}/api/volumes/0/performance?unit=SECONDS&limit=1'.format(array_url)
    get_json_stats = get_data(volume_stats, api_token)
    for stats in get_json_stats:
        for key in performance_metrics:
            metric = '{}.array_stats.{}'.format(array_name, key)
            if 'throughput' in key:
                metric_value = stats[key]['size_in_bytes']
            else:
                metric_value = stats[key]
            send_to(metric, metric_value)


def send_to(metric, metric_value, timestamp=None):
    '''(str, float) -> str|None
    it sends to graphite or print to standard
    output the passed metrics.

    >>> send_to(volume_space.vol_ppcmeta_221.volumes, 718848)
    '''

    if timestamp:
    		timestamp = timestamp / 1000

    if to_graphite is True:
        graphyte.send(metric, metric_value,timestamp)
    else:
        print('{}.{} {} {}'.format(metric_root, metric, metric_value, timestamp))


def main():

    # Initialize graphite
    graphyte.init(graphite_server_address, graphite_server_port, prefix=metric_root)

    # Run the collectors
    array_stats(array_name,array_url,api_token)
    # volume_stats(array_name,array_url, api_token)


if __name__ == "__main__":
    main()
