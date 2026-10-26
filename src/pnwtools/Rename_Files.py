"""
`pnwtools.Rename_Files`

Script to rename files in a directory tree. Retains time and date info if 
present in the filename. If not, generates a comparable timestamp based on when 
the file was last modified.
"""

import argparse
import os
import pandas as pd
import sys
import wave

from datetime import datetime, timedelta
from pathlib import Path

from pnwtools.utils.file import find_files
from pnwtools.utils.info import recite_list
from pnwtools.utils.lists import has_duplicates
from pnwtools.utils.naming import *


def _build_parser():
    parser = argparse.ArgumentParser(description="Intelligently rename files within a target directory.")

    parser.add_argument("target_dir", 
                        nargs='?', 
                        default=os.getcwd(),
                        type=str,
                        help="Directory containing files to be renamed. Default: Current working directory.")


    parser.add_argument("-p", "--prefix",
                        dest="prefix",
                        type=str,
                        default="%g-%c",
                        help="Prefix to use. May include wildcards which will be dynamically applied based on each file's folder location. Acceptable wildcards include `%%p` (parent folder name), `%%g` (grandparent folder name), `%%c` (last component of the parent folder name), and `%%h` (last component of the grandparent folder name). Combine these wildcards with arbitrary strings to structure filenames how you like. Default: `%%g-%%c`.")


    parser.add_argument("-d", "--dry-run",
                        dest="dry_run",
                        action="store_true",
                        help="Preview mode. Files will not be renamed. A dummy log file will be generated showing expected results of the specified renaming operation.")


    parser.add_argument("-e", "--extensions",
                        dest="extensions", 
                        type=str,
                        default="wav",
                        help="List of file extensions of files to rename. Extensions do not need to begin with a dot and are not case-sensitive (e.g. '.wav', and 'WAV' will be handled the same). If specifying multiple extensions, separate extensions with commas, e.g. `wav,flac`. Default: wav.")


    parser.add_argument("-n", "--number-files",
                        dest="number_files",
                        action="store_true",
                        help="Number files sequentially. Resulting filenames will consist only of a prefix and a serial number, ignoring any timestamps present in the current filenames. Not recommended for audio data.")


    parser.add_argument("-a", "--allow-duplicates",
                        dest="allow_duplicates",
                        action="store_true",
                        help="Allow renaming to create duplicate filenames. Not recommended for audio data.")


    parser.add_argument("-m", "--use-modtime",
                        dest="use_mod_time",
                        action="store_true",
                        help="Generate a timestamp for each file from the file's last modification time.")


    parser.add_argument("-c", "--use-createtime",
                        dest="use_create_time",
                        action="store_true",
                        help="Generate a timestamp for each file from the file's creation time.") 


    parser.add_argument("-w", "--use-wav-metadata",
                        dest="use_wav_metadata",
                        action="store_true",
                        help="Generate a timestamp for each file from WAMD or GUANO metadata (WAV files only).")


    parser.add_argument("-z", "--timezone",
                        dest="time_zone",
                        type=str,
                        help="Specify the correct time zone for interpreting file creation or modification times. Availability depends on your machine's time zone definitions. You can specify a time zone by name, e.g. 'US/Eastern' or 'America/Los_Angeles'. Be advised that many of these time zones automatically adjust for daylight saving time (DST), which may not be what you want. You can also specify a time zone relative to Greenwich Mean Time / Univeral Coordinated Time, use e.g. 'Etc/GMT-7'; time zones specified this way will not account for DST. Default: System time zone.")


    parser.add_argument("-o", "--offset",
                        dest="time_offset",
                        type=int,
                        default=0,
                        help="Add a fixed offset (hours; may be positive or negative) to the existing or constructed timestamp for each file.")

    return parser


def main():

    run_date = datetime.now()
    parser = _build_parser()
    args = parser.parse_args()

    target_dir = Path(args.target_dir)
    dir_name = target_dir.name
    ext_list = args.extensions.split(',')
    prefix = args.prefix
    number_files = True if args.number_files else False

    matched_files = find_files(target_dir, ext_list)
    print(f"\nFound {len(matched_files):,} {recite_list(ext_list)} files.")

    rename_info = prep_mass_rename(matched_files, prefix, number_files=number_files)
    new_names = [i[2] for i in rename_info]

    if has_duplicates(new_names):
        print("\nRenaming operation would result in duplicate filenames!")
        if args.allow_duplicates or args.dry_run:
            pass
        else:
            print("\nRenaming aborted. Use -a to allow duplicate filenames (not recommended).\n")
            exit()

    n_changes = sum([i[-1] for i in rename_info])

    info_df = pd.DataFrame(data=rename_info, 
                           columns=["Folder","Old_Name","New_Name","Change"])

    verb = "would" if args.dry_run else "will"
    print(f"\nRenaming {verb} affect {n_changes:,} of {len(matched_files):,} filenames.")

    if args.dry_run:
        out_file = Path(target_dir, f"{dir_name}_rename_PREVIEW.csv")
        info_df.to_csv(out_file, index=False)
        print(f"\nPreview written to {out_file.name}.\n")
    elif n_changes > 0:
        out_file = Path(target_dir, f"{dir_name}_Rename_Log_{run_date:%Y%m%d}.csv")
        result = mass_rename(rename_info)
        result_df = info_df[["Folder", "Old_Name", "New_Name"]]
        result_df["Result"] = result
        result_df.to_csv(out_file, index=False)
        print(f"\nRenaming complete. Changes logged to {out_file.name}.\n")
    else:
        print("\nExiting...\n")

    exit()


if __name__ == "__main__":
    main()
