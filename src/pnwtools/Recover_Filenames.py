"""
Script to try and recover the names of .wav files based on Wildlife 
Acoustics WAMD and/or Guano-formatted metadata and/or recording date.
\n\n**Arguments:**

``target_dir``: Path to the directory containing WAV files to be 
recovered. Required.

``-p <prefix>`` or ``--prefix <prefix>``: Prefix to use in files 
recovered by this script. Optional; if not provided, the ARU serial 
number of each file will be used instead.

``-d`` or ``--dry-run``: Preview changes without actually renaming any
files.

**Output:**

    A CSV file listing the original and new name of each file with a 
    column indicating whether each file was actually renamed. Will be
    created in the target directory.

**Usage:**

    ``python -m Recover_Filenames.py <target_dir> -p <prefix> -d``

    e.g.

    ``python -m Recover_Filenames.py E:\Recovered_Files -p KLA_16324``
"""


import argparse
import os
import pandas as pd
import re
import sys
from datetime import datetime
from pathlib import Path
from pnwtools.utils.file import find_files
from pnwtools.utils.metadata import *
from pnwtools.utils.naming import *


def _build_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument("target_dir", 
                        nargs='?', 
                        default=os.getcwd(), 
                        type=str,
                        help="Path to the directory containing recovered audio files. Default: Current working directory.")

    parser.add_argument("-p", "--prefix",
                        dest="prefix",
                        type=str,
                        help="Prefix for recovered files. Default: ARU serial number from metadata.")

    parser.add_argument("-d", "--dry-run",
                        dest="dry_run",
                        action="store_true",
                        help="Preview changes but do not actually rename files.")

    return parser


def main():
    parser = _build_parser()
    args = parser.parse_args()

    top_dir = Path(args.top_dir)

    wavs = find_files(top_dir, 'wav')

    to_recover = [w for w in wavs if re.match("File[0-9]+\\.[Ww][Aa][Vv]", w.name)]

    print(f"\nFound {len(to_recover)} files in need of renaming.")

    wav_info = [get_metadata(w) for w in to_recover]

    rename_info, failed_info = [], []
    to_rename = 0

    for w in wav_info:
        folder, name_orig = w['dir'], w['name']

        new_prefix = args.prefix if args.prefix else w['serial']
        meta_stamp = w['stamp']
        try:
            str_stamp = format_stamp(meta_stamp)
        except:
            str_stamp = ''

        new_name = build_filename(new_prefix, str_stamp)

        if new_prefix == '' or meta_stamp == '':
            failed_info.append((folder, name_orig, new_name))
        else:
            is_diff = 1 if name_org == new_name else 0
            rename_info.append((folder, name_orig, new_name))

    rename_df = pd.DataFrame(data=rename_info, 
                             columns=["Folder","Old_Name","New_Name"])

    if not args.dry_run:
        result = mass_rename(rename_info)
        rename_df["Result"] = result

        n_renamed = len(rename_log_df[rename_log_df["Result"] == 1])
        n_errors = len(rename_log_df[rename_log_df["Result"] == -1])
        n_not_attempted = len(failed_info)

        print(f"\n{n_renamed} files successfully renamed.")
        if n_failed > 0:
            print(f"\n{n_errors} renaming attempts were unsuccessful.")
        
        if len(failed_info) > 0:
            print(f"\nCould not recover sufficient metadata for {n_not_attempted} files.")   
    else:
        pass

    with open(os.path.join(top_dir, "Rename_Log.csv"), 'w') as logfile:
        logfile.write("Old_name,New_name\n")
        logfile.write('\n'.join(log_lines))


if __name__ == '__main__':
    main()
