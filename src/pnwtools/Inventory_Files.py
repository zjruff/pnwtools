"""
`pnwtools.Inventory_Files`

Script to build an inventory of audio files within a folder or on a drive. 
Geared toward running on folders representing sampling hexagons with one or
more recording stations, or a set of such folders located on a hard drive (or
in a folder representing a hard drive, e.g. on a server).

"""

import argparse
import os
import sys
from pathlib import Path
from pnwtools.inventory import *


def _build_parser():
    parser = argparse.ArgumentParser(description="Inventory a hex-level folder or a full hard drive.")


    parser.add_argument("target_dir", 
                        nargs='?', 
                        default=os.getcwd(), 
                        type=str,
                        help="Directory or drive containing audio files to be inventoried. Default: Current working directory.")

    parser.add_argument("-l", "--label", 
                        dest="label", 
                        type=str, 
                        help="Label to apply to output files (default: name of target dir).")

    parser.add_argument("-d", "--drive-mode", 
                        dest="drive_mode", 
                        action="store_true",
                        help="Inventory entire drive. Find hex-level dirs automatically and partition output by hex.")

    parser.add_argument("-f", "--full-inv", 
                        dest="save_full_inv", 
                        action="store_true",
                        help="Save full inventory in addition to streamlined CSV output.") 

    parser.add_argument("-k", "--skip-metadata",
                        dest="skip_metadata", 
                        action="store_true",
                        help="Skip metadata (Do not attempt to extract WAV file metadata, e.g. ARU serial numbers).")

    parser.add_argument("-e", "--extensions", 
                        dest="inv_extensions", 
                        type=str,
                        help="List of file extensions to include in inventory. By default, only WAV files will be included. Any audio file format that `soundfile` can handle is fair game, but inventorying large numbers of non-WAV audio files may be slow. Extensions do not need to begin with a period and are not case-sensitive (e.g. '.wav', and 'WAV' will be handled the same). If specifying multiple extensions, separate extensions with commas, e.g. ""wav,flac"".", default="wav")

    return parser


def main():

    parser = _build_parser()

    args = parser.parse_args()

    target_dir = Path(args.target_dir)

    if not args.label:
        output_name = target_dir.name
    else:
        output_name = args.label

    ext_list = args.inv_extensions.split(' ')
    incl_meta = True if not args.skip_metadata else False
    drive_mode = False if not args.skip_metadata else True

    print(f"\nCreating file inventory for {output_name}.") 

    inv_out_path = Path(target_dir, f"{output_name}_inventory.csv")

    inv_df_full = build_file_inventory(target_dir, meta=incl_meta, ext_list=ext_list)

    report_inv_stats(inv_df_full)

    if args.save_full_inv:
        full_inv_path = Path(target_dir, f"{output_name}_inventory_full.csv")
        inv_df_full.to_csv(full_inv_path, index=False)

    inv_df = format_inventory(inv_df_full)

    inv_df.to_csv(inv_out_path, index=False)
    print(f"\nInventory saved to {str(inv_out_path)}.\n")


if __name__ == "__main__":
    main()
