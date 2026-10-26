"""
`pnwtools.utils.pnw`

Defines functions whose purpose is more or less specific to acoustic monitoring
by the U.S. Forest Service under the Northwest Forest Plan (NWFP) Effectiveness 
Monitoring Program.

Functions:

    check_filename
        Check whether a filename conforms to PNW formatting expectations.

    combine_meta_files
       Combine Kaleidoscope meta.csv files within a folder into one dataframe. 

    find_hex_dirs
        Enumerate hex-level folders within another folder, including a hard 
        drive or other device.

    parse_filename
        Extract information (timestamp, date, prefix, hex) from a filename.

    read_meta_file
        Read a `meta.csv` file produced by Kaleidoscope during scanning, 
        clustering, SPL analysis, and other operations. 
"""

import os
import pandas as pd
import re
import sys
from pathlib import Path
from ..naming import *
from .spectro import *


def check_filename(file_path):
    """Check whether a filename conforms to PNW formatting expectations.

    The filename should begin with a prefix that matches the two lowest-level 
    components of the directory path and end with a timestamp in format 
    YYYYMMDD_HHMMSS.

    Args:

        file_path (pathlib.Path): Path to an audio file.

    Returns:

        tuple: A 3-tuple. The first element is True if the file's prefix 
        matches what is expected based on the directory structure, the second
        element is True if the filename ends with a timestamp in the correct
        format, and the third element is True if the filename consists only
        of these two components separated by an underscore.
    """

    file_path = Path(file_path)
    dirname, filename = file_path.parent, file_path.stem

    hex_part, stn_part = dirname.parts[-2:]
    stn_id = re.split("[\\-_ ]", stn_part)[-1]
    dir_prefix = f"{hex_part}-{stn_id}"

    file_vals = parse_filename(filename)

    prefix_correct = (file_vals["Prefix"] == dir_prefix)

    stamp_correct = (file_vals["Str_Stamp"] != '')

    pred_filename = f"{file_vals['Prefix']}_{file_vals['Str_Stamp']}"
    structure_correct = (pred_filename == filename)

    return (prefix_correct, stamp_correct, structure_correct)


def combine_meta_files(top_dir):
    """Combine Kaleidoscope meta.csv files within a folder into one dataframe.

    Args:

        top_dir (pathlib.Path or str): Path to a directory containing
            Kaleidoscope output files from one or more datasets.

    Returns:

        tuple: A tuple containing the list of meta.csv files that were found 
        and a pandas.DataFrame containing information from those files.
    """

    meta_files = [x for x in noise_dir.rglob("*") if x.name=="meta.csv"]

    meta_df_list = [read_meta_file(x) for x in meta_files]

    meta_df = pd.concat(meta_df_list, axis=0)

    meta_df.drop_duplicates(subset=["IN_FILE", "DURATION", "SERIAL_NO"], inplace=True)

    return (meta_files, meta_df)


def find_hex_dirs(drive_path):
    """Locate hex-level folders within a drive-level folder.

    On a Windows machine it should be possible to simply specify the drive 
    letter, e.g. 'F' or 'f', so that this will run on arbitrary removable 
    storage devices.

    Args:

        drive_path (pathlib.Path or str): Drive letter or mount point for the
            drive where the hex directories are located.

    Returns:

        list: List of paths representing hex-level folders on the hard drive.
    """

    try:
        drive_path.upper()
    except:
        drive_path = Path(drive_path)

    drive_contents = Path(drive_path).glob("*")

    hex_pattern = "[A-Z]+_[A-Za-z0-9]+$"
    
    hex_dirs = [d for d in drive_contents if d.is_dir() and re.match(hex_pattern, d.name)]

    return sorted(hex_dirs)


def parse_filename(filename):
    """Extract information (timestamp, date, prefix, hex) from a filename.

    Args:

        filename (str): A string representing a filename without its file 
            extension. 

    Returns:

        dict: Dictionary of string values, "Hex", the combination of area and 
        hex ID (e.g. "CAS_15141"), "Prefix", combination of area, hex ID, and 
        station ID (e.g. "CAS_13967-C"), "Str_Stamp", a full date-time stamp in 
        format YYYYMMDD_HHMMSS (e.g. "20260415_075202"), and "Str_Date", the 
        date portion of the date-time stamp (e.g. "20260415").
    """

    if Path(filename).suffix != '':
        filename = Path(filename).stem

    hex_match = re.search("^[A-Z]+_[0-9A-Za-z]+(?=-)", filename)
    file_hex = hex_match.group(0) if hex_match else ''

    prefix_match = re.search("^[A-Z]+_[0-9A-Za-z]+-[A-Z0-9]+", filename)
    file_prefix = prefix_match.group(0) if prefix_match else ''

    stamp_match = re.search("20[0-9]{6}_[0-9]{6}$", filename)
    file_stamp = stamp_match.group(0) if stamp_match else ''

    date_match = re.search("(?<=_)20[0-9]{6}(?=_)", filename)
    file_date = date_match.group(0) if date_match else ''

    info_dict= {"Hex": file_hex, "Prefix": file_prefix, 
                "Str_Stamp": file_stamp, "Str_Date": file_date}

    return info_dict


def read_meta_file(meta_file_path):
    """Read and format a meta.csv file produced by Kaleidoscope.

    Args:

        meta_file_path (pathlib.Path or str): Path to the meta.csv file.

    Returns:

        pandas.DataFrame: A data frame listing the input directory, relative
        path, filename, duration, recording date and time, latitude and 
        longitude, ARU model, and ARU serial number. 
    """

    meta_df = pd.read_csv(meta_file_path)

    meta_df.rename(mapper=lambda x: x.replace(' ', '_'), axis=1, inplace=True)

    return meta_df[["INDIR", "FOLDER", "IN_FILE", "DURATION", "DATE", "TIME",
                    "LATITUDE", "LONGITUDE", "MODEL", "SERIAL_NO"]]
