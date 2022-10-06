#!/usr/bin/env python3
import argparse
import sys
import time
import os
from datetime import datetime
from dateutil import tz
from dateutil.parser import parse

resolutions = {
    'nanos': int(1e17),
    'micros': int(1e14),
    'millis': int(1e11),
    'seconds': 0
}
default_ozones = os.getenv('DEFAULT_OZONES', 'UTC,Local').split(',')

parser = argparse.ArgumentParser(description='Convert time(s) to UTC')
parser.add_argument('-i', '--izone', help='parse input as this IANA timezone', default="UTC")
parser.add_argument('-f', '--format', help='output format', default="%a %Y-%m-%d %H:%M:%S.%f")
parser.add_argument('-l', '--local', action='store_true', help='parse input using local timezone. overrides -i')
parser.add_argument('-o', '--ozones', nargs='*', help='convert to these IANA timezones', default=[])
parser.add_argument('-d', '--default-ozones', nargs='*', help='default ozones', default=default_ozones)
parser.add_argument('-v', '--tzformat', help='format for timezones', choices=['file', 'short'], default='short')
parser.add_argument('time', nargs='*', default=[time.time_ns()])

def format_tz(tz, dt, tzformat, izone):
    res = ''
    if tzformat == 'file':
        res = tz._filename
    else:
        res = tz.tzname(dt)

    if tz == izone:
        return f"[{res}]"

    return res

def print_time(t, izone, ozones, format, tzformat):
    try:
        num = int(t)
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
        date = parse(t)
        if date.tzinfo is None:
            date = date.replace(tzinfo=izone)
        nanos = int(date.timestamp() * 1e9)

    for i, k in enumerate(resolutions.keys()):
        if k == ty:
            f = f'[{k}]'
        else:
            f = f'{k}'
        print(f, nanos // (10 ** (3 * i)), end=' ')
    print()

    seconds = nanos // int(1e9)
    nanopart = nanos % int(1e9)

    out = [] # for column formatting
    for tz in ozones:
        date = datetime.fromtimestamp(seconds, tz=tz)
        format = format.replace('%f', str(nanopart))
        formatted = date.strftime(format)
        formattedtz = format_tz(tz, date, tzformat, izone)
        out.append((formattedtz, formatted))

    maxtzname = max([len(tz) for (tz, _) in out]) 
    for (tz, d) in out:
        print(f"{tz:{maxtzname}}: {d}")

if __name__ == "__main__":
    args = parser.parse_args()

    izone = tz.gettz() if args.local else tz.gettz(args.izone)
    if izone is None:
        print('invalid izone', izone)
        exit(1)

    ozones = []
    for oz in args.ozones + args.default_ozones:
        if oz == 'Local':
            oz = None
        ozone = tz.gettz(oz)
        if ozone is None:
            print('invalid ozone', oz)
        ozones.append(ozone)
    
    for t in args.time:
        print_time(t, izone, ozones, args.format, args.tzformat)

