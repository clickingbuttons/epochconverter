#!/usr/bin/env python3
import sys
import time
import os
from datetime import datetime, timezone
from dateutil.parser import parse

resolutions = {
    'nanos': int(1e17),
    'micros': int(1e14),
    'millis': int(1e11),
    'seconds': 0
}

tzs = [
    'UTC', # first zone is working zone
    'US/Eastern'
]

if __name__ == "__main__":
    os.environ['TZ'] = tzs[0]
    time.tzset()

    if len(sys.argv) == 1:
        sys.argv.append(time.time_ns())
    
    try:
        num = int(sys.argv[1])
        ty = 'seconds'
        for i, (k, v) in enumerate(resolutions.items()):
            if num >= v:
                ty = k
                nanos = num * (10 ** (3 * i))

        if num >= 1e17:
            ty = 'nanos'
            nanos = num
        elif num >= 1e14: # stolen from epochconverter.com
            ty = 'micros'
            nanos = num * int(1e3)
        elif num >= 1e11: # stolen from epochconverter.com
            ty = 'millis'
            nanos = num * int(1e6)
        else:
            ty = 'seconds'
            nanos = num * int(1e9)


    except ValueError:
        ty = 'datestring'
        date = parse(sys.argv[1])
        nanos = int(date.strftime('%s')) * int(1e9)

    for i, k in enumerate(resolutions.keys()):
        if k == ty:
            f = f'[{k}]'
        else:
            f = f'{k}'
        print(f, nanos // (10 ** (3 * i)), end=' ')
    print()

    seconds = nanos // int(1e9)
    nanopart = nanos % int(1e9)

    for tz in tzs:
        os.environ['TZ'] = tz
        time.tzset()
        date = datetime.fromtimestamp(seconds)
        print(f"{tz}: {date}.{nanopart}")

