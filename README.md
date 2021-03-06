# analyze_lnd_htlc
## Introduction

Rebalancing channels is an important part of running a Lightning Network node. While it would be great if all channels could be rebalanced, rebalancing requires outbound capacity, which is limited, so it is necessary to determine which channels are in demand.

Well routed channels are in demand. However, it is not enough to identify the channels that are truly in demand; you also need to look at the channels that you have tried to route but failed. Such failures cannot be detected just by running the node normally, but if we can take action, we can expect more routing.

This script analyzes the json file generated by [stream-lnd-htlc](https://github.com/smallworlnd/stream-lnd-htlcs) and displays the data of both successful and unsuccessful routes to help us determine which channels are in demand.

## Installation
### stream-lnd-htlc
This tool requires the json file generated by [stream-lnd-htlc](https://github.com/smallworlnd/stream-lnd-htlcs), so please install and run it first.

### analyze_lnd_htlc itself
Download the project from git by executing the following command.

    git clone https://github.com/Marimox/analyze_lnd_htlc
    cd analyze_lnd_htlc
    pip3 install -r requirements.txt

## Usage
### Command line arguments

    usage: analyze_lnd_htlc.py [-h] [-i INPUT_FILE] [-s START_DATETIME]
                               [-e END_DATETIME]
    
    optional arguments:
      -h, --help            show this help message and exit
      -i INPUT_FILE, --input_file INPUT_FILE
                            Input json file generated by stream-lnd-htlcs.
      -s START_DATETIME, --start_datetime START_DATETIME
                            Analysis start datetime. Datetime must be in ISO format. 
                            For example: 2021-10-17 00:00:00
      -e END_DATETIME, --end_datetime END_DATETIME
                            Analysis end datetime. Datetime must be in ISO format.
                            For example: 2021-10-17 23:59:59
