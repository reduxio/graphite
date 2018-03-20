# Reduxio Collector Script for Graphite

This collector script enables administrators to monitor their Reduxio systems using Graphite.
Various metrics from the Reduxio system are collected using Reduxio REST API and
are added to the Graphite database. This is useful for long term monitoring.

The script collects the following metrics tree:

 - storage
	 - reduxio
	 - \<array name\>
		 - array_stats
			 - io_read
			 - io_write
			 - io_total
			 - throughput_read (bytes)
			 - throughput_write (bytes)
			 - throughput_total (bytes)
			 - latency_read (milliseconds)
			 - latency_write (milliseconds)
			 - latency_total (milliseconds)
		 - volume_stats
			 - \<volume name\>
				 - io_read
				 - io_write
				 - io_total
				 - throughput_read (bytes)
				 - throughput_write (bytes)
				 - throughput_total (bytes)
				 - latency_read (milliseconds)
				 - latency_write (milliseconds)
				 - latency_total (milliseconds)
	 
	 
	 

## Requirements

1. Reduxio HX Series system running Reduxio TimeOS v3.3 or higher.
2. Graphite v0.9 or higher: For easy installation and deployment, use [docker-graphite-statsd Docker Image](https://hub.docker.com/r/graphiteapp/docker-graphite-statsd/).
3. Optional: Grafana for visualizing the data - See the official [Grafana Docker image](https://hub.docker.com/r/grafana/grafana/)
4. `graphyte` python module.
5. `requests` python module.

## Installation

Copy the example collector script (reduxio_collector.py) to a dedicated host.

## Configuration
The following parameters are configurable in `reduxio_collector.py` script:

|Parameter Name                |Description                          |
|----------------|-------------------------------|
|`metric_root`|Root metric prefix for identifying Reduxio's related metrics.       |
|`graphite_server_address`          | IP/FQDN of the graphite server           |
|`graphite_server_port`          |Graphite server port|
|`array_url`          |URL (IP/FQDN) of the Reduxio array to collect stats from|
|`array_name`          |Name of the array. Used to identify the array in the metrics tree|
|`api_token`          |API Token of the TimeOS REST API.  Use the following URL to create a Token in TimeOS:  https://reduxio_system_address/#/app/settings/api-tokens.|
|`to_graphite`          |Useful for debugging. Set to 'True' to enable data transfer to Graphite, or false to print requests to STDOUT|


## Usage
	shell> ./reduxio_collector.py
This will collect the current seconds granularity metrics for the entire array and per volume. It is recommended to run the script as a cron job with the desired sample interval.

