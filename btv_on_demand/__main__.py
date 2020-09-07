import os
import sys
import time
from datetime import datetime

import schedule

from . import INTERVAL_H
from .ingest import main_ingest

def do_ingest():

    try:
        main_ingest(sys.argv)
    except Exception as e:
        print(f'Ingest failed: {e}')
    else:
        print('Ingest complete')

if (__name__ == '__main__'):

    print('')
    print(f'Ingest scheduled every {INTERVAL_H} hours')
    schedule.every(INTERVAL_H).hours.do(do_ingest)

    try:
        # Run once initially
        schedule.run_all()

        while True:
            schedule.run_pending()

            print(f'Next ingest will run at {schedule.next_run()}')
            time.sleep(schedule.idle_seconds())

    except KeyboardInterrupt:
        sys.exit(0)
