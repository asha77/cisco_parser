import os
import pathlib
from regparsers import *

def devices_summary_output(number, filename, config: object):
    print('| {0:4d} | {1:75s} | {2:25s} | {3:15s} | {4:20s} | {5:18s} |  {6:10s} | {7:12s} |'.format(
            number+1,
            filename,
            obtain_hostname(config),
            obtain_mng_ip_from_config(config),
            obtain_domain(config),
            obtain_model(config),
            obtain_serial(config),
            obtain_software_version(config))
            )
