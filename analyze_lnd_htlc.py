#!/usr/bin/env python3

import argparse
import sys
import datetime
import json
import pandas as pd

class Analyze:
    def __init__(self, arguments):
        self.arguments = arguments

    def init_dataframe(self):
        with open(self.arguments.input_file, 'r') as f:
            data = []
            for line in f:
                row = json.loads(line)

                prev_incoming_amt = 0
                prev_outgoing_amt = 0

                if row['event_type'] == 'FORWARD':
                    if row['event_outcome'] == 'link_fail_event':
                        data.append(
                            (
                                row['timestamp'],
                                row['incoming_peer'],
                                row['outgoing_peer'],
                                row['event_outcome'],
                                row['failure_detail'],
                                row['outgoing_channel_capacity'],
                                row['outgoing_channel_local_balance'],
                                int(row['event_outcome_info']['incoming_amt_msat']) / 1000,
                                int(row['event_outcome_info']['outgoing_amt_msat']) / 1000,
                            )
                        )
                    elif row['event_outcome'] == 'forward_event':
                        prev_incoming_amt = int(row['event_outcome_info']['incoming_amt_msat']) / 1000
                        prev_outgoing_amt = int(row['event_outcome_info']['outgoing_amt_msat']) / 1000
                    elif prev_incoming_amt > 0 and prev_outgoing_amt > 0:
                        data.append(
                            (
                                row['timestamp'],
                                row['incoming_peer'],
                                row['outgoing_peer'],
                                'forward_event',
                                row['event_outcome'],
                                row['outgoing_channel_capacity'],
                                row['outgoing_channel_local_balance'],
                                prev_incoming_amt,
                                prev_outgoing_amt,
                            )
                        )

            df = pd.DataFrame(data, columns=['timestamp', 'incoming_peer', 'outgoing_peer', 'event', 'detail', 'out_capacity', 'out_local_amt', 'in_amt', 'out_amt'])
            pd.set_option('display.max_rows', 1000)
            pd.options.display.float_format = '{:.3f}'.format
        
            df['timestamp'] = pd.to_datetime(df['timestamp'].astype(int), unit='s')
            df.set_index('timestamp', inplace=True)

            if self.arguments.start_datetime and self.arguments.end_datetime:
                df = df.loc[self.arguments.start_datetime:self.arguments.end_datetime]

            df['fee'] = df['in_amt'] - df['out_amt']

            return df

    def start(self):
        df = self.init_dataframe()

        print('')
        print('------------------------------------------------------------')
        print('1. FORWARD EVENT SUMMARY (OUTGOING PEER)')
        print('------------------------------------------------------------')
        print('')
        df_summary_out = df.groupby(['outgoing_peer', 'event', 'detail'])['out_amt'].agg(['count', 'sum', 'min', 'max', 'mean', 'std']) \
            .rename(columns={'sum':'outgoing_total', 'min':'outgoing_min', 'max':'outgoing_max', 'mean':'outgoing_mean', 'std':'outgoing_std'})
        df_summary_fee = df.groupby(['outgoing_peer', 'event', 'detail'])['fee'].agg(['sum', 'min', 'max', 'mean', 'std']) \
            .rename(columns={'sum':'fee_total', 'min':'fee_min', 'max':'fee_max', 'mean':'fee_mean', 'std':'fee_std'})
        print(pd.merge(df_summary_out, df_summary_fee, on=['outgoing_peer', 'event', 'detail']))
        print('')
        print('------------------------------------------------------------')
        print('2. FORWARD EVENT SUMMARY (INCOMING PEER)')
        print('------------------------------------------------------------')
        print('')
        df_summary_in = df.groupby(['incoming_peer', 'event', 'detail'])['in_amt'].agg(['count', 'sum', 'min', 'max', 'mean', 'std']) \
            .rename(columns={'sum':'incoming_total', 'min':'incoming_min', 'max':'incoming_max', 'mean':'incoming_mean', 'std':'incoming_std'})
        print(df_summary_in)
        print('')        
        print('------------------------------------------------------------')
        print('3. LINK FAIL EVENT DETAIL')
        print('------------------------------------------------------------')
        print('')
        df_detail_link_fail_event = df.query('event == "link_fail_event"')
        print(df_detail_link_fail_event[['incoming_peer', 'outgoing_peer', 'detail', 'out_capacity', 'out_local_amt', 'out_amt', 'fee']])
        print('')

        return 

def main():
    argument_parser = get_argument_parser()
    arguments = argument_parser.parse_args()
    return Analyze(arguments).start()

def datetime_type(datetime_str):
    return datetime.datetime.fromisoformat(datetime_str)

def get_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i',
        '--input_file',
        dest='input_file',
        help='Input json file generated by stream-lnd-htlcs.',
    )
    parser.add_argument(
        '-s',
        '--start_datetime',
        dest='start_datetime',
        type=datetime_type,
        help='Analysis start datetime. '
                'Datetime must be in ISO format. For example: 2021-10-17 00:00:00',
    )
    parser.add_argument(
        '-e',
        '--end_datetime',
        dest='end_datetime',
        type=datetime_type,
        help='Analysis end datetime. '
                'Datetime must be in ISO format. For example: 2021-10-17 23:59:59',
    )
    return parser

success = main()
if success:
    sys.exit(0)
sys.exit(1)
