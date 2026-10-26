"""
`pnwtools.utils.naming.timestamp`

Defines functions specifically related to timestamps.

Functions:

    adjust_stamp
        Change a timestamp by adding a fixed offset. 

    build_stamp_from_mtime
        Return a file's modification time as a formatted string.

    format_stamp
        Convert a datetime value to a string in YYYYMMDD_HHMMSS format.

    get_timestamp
        Extract a timestamp from a properly formatted filename.

    parse_stamp
        Convert a string-formatted timestamp to a functioning datetime value.

    update_time_zone
        Change a timestamp to reflect a change in time zone.
"""

import os
import re
import time
from datetime import datetime, timedelta


# Local time zone in hours relative to GMT / UTC
SYS_TZ_OFFSET = time.localtime().tm_gmtoff / 3600.


def adjust_stamp(stamp_orig, offset=None, time_zone=None, orig_time_zone=None):
    """Adjust a timestamp by a fixed offset or to a specific time zone.

    Args:

        stamp_orig (datetime.datetime): The timestamp to be adjusted.

        offset (int or datetime.timedelta): Adjustment to apply to the original 
            timestamp. If this is an integer value, it will be treated as a
            number of hours. If it is a datetime.timedelta object, the 
            difference can be specified in various ways; see documentation for
            the `datetime` package for details.

        time_zone (str): String representing the time zone that should apply to
            the timestamp provided. By default, the function will adjust the 
            timestamp according to the difference between the current system
            time zone and the time zone specified.

        orig_time_zone (str): String representing the time zone under which the
            timestamp was created.

    Returns:

        datetime.datetime: A new timestamp created by applying any necessary 
        adjustments to the original timestamp.
    """

    if offset:
        new_stamp = stamp_orig + timedelta(hours=offset)
    elif time_zone:
        if time_zone_orig:
            new_stamp=update_time_zone(stamp_orig, time_zone, time_zone_orig)
        else:
            new_stamp=update_time_zone(stamp_orig, time_zone)
    else:
        new_stamp = stamp_orig

    return new_stamp


def build_stamp_from_stats(file_path, use_stat="mod"):
    """Return a file's modification time as a formatted string.

    Args:

        file_path (pathlib.Path or str): Path to a file.

        use_stat (str): String representing which file stat to use Either "modification" or "creation", or shortened 
            versions thereof.

    Returns:

        datetime.datetime: datetime object representing the file's creation or
        modification time.
    """

    stamp = datetime.fromtimestamp(os.path.getmtime(file_path))

    str_stamp = format_stamp(stamp)

    return str_stamp


def format_stamp(datetime):
    """Convert a datetime value to a string in YYYYMMDD_HHMMSS format."""

    str_stamp = f"{datetime:%Y%m%d_%H%M%S}"

    return str_stamp


def get_timestamp(filename):
    """Extract a timestamp from a properly formatted filename.

    Args:

        filename (str): Filename that may or may not include a timestamp.

    Returns:

        str: String representing a timestamp in YYYYMMDD_HHMMSS format, or an
        empty string ('') if the filename does not contain a timestamp in this
        format.
    """

    stamp = re.search("20[0-9]{6}_[0-9]{6}", filename)
    if stamp:
        str_stamp = stamp.group()
    else:
        str_stamp = ''

    return str_stamp


def parse_stamp(str_stamp, fmt="%Y%m%d_%H%M%S"):
    """Convert a string-formatted timestamp to a functioning datetime value.

    By default this is set up to handle timestamps as created by Wildlife 
    Acoustics ARUs and the default format is YYYYMMDD_HHMMSS, e.g. 
    "20261006_153502" for 15:35:02 on 6 Oct 2026.

    Args:

        str_stamp (str): String representing a timestamp in YYYYMMDD_HHMMSS 
            format.

        fmt (str): Format string to be passed to datetime.datetime.strptime.

    Returns:

        datetime.datetime: A datetime value derived from the timestamp string.
    """

    stamp = datetime.strptime(str_stamp, fmt)

    return stamp


def update_time_zone(dt_orig, tz_new, tz_orig=None):
    """Adjust a timestamp to reflect differences between time zones.

    Args:

        dt_orig (datetime.datetime): datetime object representing a timestamp 
            to be adjusted.

        tz_new (str): String representing the time zone to be applied to the 
            datetime.

        tz_orig (str): String representing a time zone reflected in the 
            original datetime object. If not specified, the current system time
            zone will be used.

    Returns:

        datetime.datetime: datetime object representing a new timestamp created
        by adjusting the original timestamp to reflect the differences between
        the new and original time zones. 
    """

    if not tz_orig:
        adj = SYS_TZ_OFFSET

    

    dt_adj = dt_orig

    return dt_adj


