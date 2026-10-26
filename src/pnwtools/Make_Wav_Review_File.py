"""
A script to generate a ``review_kscope``-style CSV file to allow us to 
look at every part of a given set of wav files.\n\n**Arguments:**

``target_dir``: Path to the directory containing .wav files. Required.

``-d <clip_length>`` or ``--duration <clip_length>``: Duration of each 
clip in seconds. Optional; default is 12.

``-i <interval>`` or ``--interval <interval>``: Spacing of clips in 
seconds. Optional; default is 12. If ``interval < clip_length``, 
successive clips will overlap. If ``interval > clip_length``, there 
will be gaps between successive clips.

**Output:**

    A CSV file listing short segments within an audio dataset, suitable
    for review and annotation using Wildlife Acoustics Kaleidoscope 
    software. Will be created in the target directory.

**Usage:**

    ``python -m MakeWavReviewFile.py [target_dir] [clip_length] [interval]``

    e.g.
    
    ``python -m MakeWavReviewFile.py E:\KLA_16234 12 8`` 
"""

import argparse
import os
import pandas as pd
import sys
from pathlib import Path
from pnwtools.tagging import build_blank_kscope_table


def _build_parser():
    parser = argparse.ArgumentParser(description="Create a table allowing for systematic browsing of a set of WAV files in Kaleidoscope by dividing the files into segments of fixed length. By default, segments will each be 12 s in length and will not overlap. Use the `-d` (duration) option to specify a length other than 12 s. Use the `-i` (interval) option to set the spacing between segments. If interval < duration, segments will overlap. If interval > duration, there will be gaps between segments. Use the `-m` (minimum duration) option to omit segments shorter than the length specified.")

    parser.add_argument("target_dir",
                        nargs='?',
                        type=str,
                        help="Path to directory containing WAV files.")

    parser.add_argument("-d", "--duration",
                        dest="seg_dur",
                        type=float,
                        default=12.0,
                        help="Duration of audio segments (seconds).")

    parser.add_argument("-i", "--interval",
                        dest="interval",
                        type=float,
                        default=12.0,
                        help="Spacing of audio segments, i.e., time (seconds) from the start of one segment to the start of the next segment.")

    parser.add_argument("-m", "--min-dur",
                        dest="min_seg_dur",
                        type=float,
                        default=6.0,
                        help="Minimum segment duration (seconds).")

    return parser


def main():

    parser = _build_parser()
    args = parser.parse_args()

    if not args.target_dir:
        target_dir = Path(os.getcwd())
    else:
        target_dir = Path(args.target_dir)

    seg_params = {"seg_dur": args.seg_dur, 
                  "interval": args.interval,
                  "min_seg_dur": args.min_seg_dur}

    kscope_table = build_blank_kscope_table(target_dir, **seg_params)

    n_lines = len(kscope_table)
    n_files = len(pd.unique(kscope_table["IN_FILE"]))
    n_folders = len(pd.unique(kscope_table["FOLDER"]))

    print(f"\nReview table includes {n_lines:,} {int(args.seg_dur)}-s segments from {n_files:,} unique WAV files in {n_folders:,} folder.") 

    dir_label = target_dir.name
    out_file = Path(target_dir, f"{dir_label}_review_full.csv")

    kscope_table.to_csv(out_file, index=False)
    print("\nTable written to file.\n")

if __name__ == "__main__":
    main()
