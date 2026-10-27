"""
`pnwtools.Generate_Spectrograms`

Generate a set of spectrogram image files representing segments of audio files
within a directory tree.

"""

import argparse
import multiprocessing as mp
import os
import pandas as pd
import sys
from datetime import datetime
from pathlib import Path
from pnwtools.utils.file import find_files
from pnwtools.utils.info import recite_list
from pnwtools.utils.pnw import *


MAX_WORKERS = mp.cpu_count()


def _build_parser():
    parser = argparse.ArgumentParser(description="Generate spectrograms representing fixed-length segments of a set of audio files using SoX.")

    parser.add_argument("target_dir",
                        nargs="?",
                        default=os.getcwd(),
                        type=str,
                        help="Directory containing audio files to be converted to spectrograms. Default: Current working directory.")

    parser.add_argument("-i", "--image_dir", 
                        dest="image_dir",
                        type=str,
                        help="Directory where images will be generated. Will be created if it does not already exist. Default: <target_dir>/Temp.")

    parser.add_argument("-d", "--dry-run",
                        dest="dry_run",
                        action="store_true",
                        help="Dry run / preview mode (generate spectrogram info file but do not actually generate spectrograms).")

    parser.add_argument("-e", "--extensions",
                        dest="extensions", 
                        type=str,
                        default="wav",
                        help="List of audio file extensions to include. Extensions do not need to begin with a dot and are not case-sensitive (e.g. '.wav', and 'WAV' will be handled the same). If specifying multiple extensions, separate extensions with commas, e.g. `wav,flac`. Default: wav.")

    parser.add_argument("-o", "--overlap",
                        dest="audio_overlap",
                        type=int,
                        default=0,
                        help="Amount of overlap in seconds between successive spectrograms. Default: 0 (spectrgrams will not overlap). Specifying a negative value will create gaps between successive spectrograms.")

    parser.add_argument("-w", "--workers",
                        dest="n_workers",
                        type=int,
                        default=MAX_WORKERS,
                        help="Number of worker processes to use while generating spectrograms. Default: Number of available (logical) cores.")

    parser.add_argument("-s", "--sox-location",
                        dest="sox_location",
                        type=str,
                        default="sox",
                        help="Location of the SoX executable. Default is `sox` (works only if SoX is on the PATH environment variable).")

    parser.add_argument("-c", "--save-csv",
                        dest="save_csv",
                        action="store_true",
                        help="Store Spectrogram_Info file as a CSV file in addition to .parquet format. (Note: Spectrogram_Info file may be large in the case of large datasets.)")

    return parser


def main():

    # Handling command-line arguments
    parser = _build_parser()
    args = parser.parse_args()

    target_dir = Path(args.target_dir)
    target_name = target_dir.name

    top_out_dir = Path(args.image_dir, target_name) if args.image_dir else Path(target_dir, "Temp")

    ext_list = args.extensions.split(',')

    # Locating audio files and building spectrogram info table

    audio_files = find_files(target_dir, ext_list)
    segment_params = {'seg_dur': 12, 'min_seg_dur': 8}
    if args.audio_overlap:
        interval = segment_params['seg_dur'] - args.audio_overlap
        segment_params['interval'] = interval 

    print(f"\nFound {len(audio_files):,} {recite_list(ext_list)} files in {target_dir}.")

    out_dirs, spectro_info = prep_spectro_gen(audio_files, top_out_dir, **segment_params)

    print(f"\n{len(spectro_info):,} spectrograms will be generated.")

    info_cols = ["Source_File", "Offset", "Duration", "Image_File"]
    spectro_info_df = pd.DataFrame(spectro_info, columns=info_cols)
    spectro_info_df = spectro_info_df.astype({"Source_File": str, "Image_File": str})

    if not top_out_dir.exists():
        top_out_dir.mkdir(parents=True)

    df_out_file = Path(top_out_dir, "Spectrogram_Info.parquet")
    spectro_info_df.to_parquet(df_out_file)

    if args.save_csv:
        df_out_csv = Path(top_out_dir, "Spectrogram_Info.csv")
        spectro_info_df.to_csv(df_out_csv, index=False)

    # Creating output directory structure and generating spectrograms

    if args.dry_run:
        print("\nSpectrogram information written to file.")

    else:
        for i in out_dirs:
            if not i.exists():
                i.mkdir(parents=True)

        proc_start = datetime.now()
        print(f"\nGenerating spectrograms starting at {proc_start:%H:%M:%S}.")

        n_workers = args.n_workers if args.n_workers else MAX_WORKERS
        with mp.Pool(n_workers) as p:
            results = p.map(generate_spectrogram, spectro_info)

        proc_end = datetime.now()
        proc_elapsed = (proc_end - proc_start).total_seconds() / 3600.
        print(f"\nFinished at {proc_end:%H:%M:%S} ({proc_elapsed:.1f} h elapsed).\n")

        err_count = sum([min(i, 1) for i in results])
        if err_count > 0:
            print(f"{err_count} spectrograms produced non-zero return codes.\n")

if __name__ == "__main__":
    main()
