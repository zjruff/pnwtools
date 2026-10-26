"""
`pnwtools.inventory`

Defines functions for building audio file inventories.

Functions:

    build_file_inventory
        Create an inventory of files in a directory tree.

    inspect_file
        Get detailed information about a single file.

    summarize_inventory
        Create a higher-level summary of a file inventory.
"""


import multiprocessing as mp
import os
import pandas as pd

from pathlib import Path
from pnwtools.utils.audio import check_audio_file
from pnwtools.utils.file import find_files
from pnwtools.utils.info import recite_list
from pnwtools.utils.metadata import get_metadata
from pnwtools.utils.naming import get_prefix, get_timestamp


MAX_WORKERS = mp.cpu_count()


def _summarize_serials(serials):

    unique_serials = set([x for x in serials if not str(x) in ["None", "nan"]])

    serial_summary = '+'.join(sorted([str(x) for x in unique_serials]))

    return serial_summary


def build_file_inventory(top_dir, ext_list=['wav'], n_workers=1, meta=True):
    """Build a table of detailed information about a set of audio files.

    Args:

        top_dir (pathlib.Path or str): Path to the root of the directory tree
            containing the audio files.

        ext_list (list): List of file extensions to be included in the 
            inventory. Any audio file format that `soundfile` can handle is
            theoretically fair game, although large numbers of non-WAV files
            may be slow to inventory. The function will only attempt to extract
            metadata from WAV files.

        n_workers (int): Number of worker processes for multiprocessing (not
            currently working).

        meta (bool): Attempt to read metadata from WAV files?

    Returns:

        pandas.DataFrame: Data frame containing detailed information about 
        audio files in the directory tree.
    """

    top_dir = Path(top_dir)

    file_paths = find_files(top_dir, ext_list)

    if n_workers == 1:
        file_info = [inspect_file(x, meta) for x in file_paths]
    else:
        to_inspect = zip(file_paths, [meta for x in file_paths])
        with mp.Pool(n_workers) as p:
            file_info = p.starmap(inspect_file, to_inspect)

    file_info_df = pd.DataFrame(data=file_info)
    rel_dirs = [str(d.relative_to(top_dir)) for d in file_info_df.dir]
    file_info_df.insert(loc=1, column="rel_dir", value=rel_dirs)

    return file_info_df


def format_inventory(inv_df):
    """Restructure a file inventory for output or display.

    Args:

        inv_df (pandas.DataFrame): Data frame listing information about a set
            of WAV files within a directory tree.

    Returns:

        pandas.DataFrame: Data frame formatted for output. The formatted 
        inventory includes "Filename", "Path" (parent directory), "Size" (file 
        size in bytes), "Duration" (file duration in seconds), and "Serial" 
        (ARU serial number from WAV metadata, if available).
    """

    out_cols = ["Filename", "Path", "Size", "Duration"]
    rename_ops = {"name": "Filename", 
                  "dir": "Path", 
                  "size": "Size",
                  "duration": "Duration"}

    if 'serial' in inv_df.columns:
        out_cols.append("Serial")
        rename_ops.update({"serial": "Serial"})

    inv_df_out = inv_df.rename(rename_ops, axis=1)[out_cols]
    
    return inv_df_out


def inspect_file(file_path, meta=True):
    """Get detailed information about a single file.

    Args:

        file_path (pathlib.Path or str): Path to the file.

        meta (bool): Attempt to read WAV file metadata from the file?

    Returns:

        dict: Dictionary listing various information about the file.
    """

    file_info = check_audio_file(file_path)
    fname_prefix = get_prefix(file_path.name)
    fname_stamp = get_timestamp(file_path.name)
    file_info.update({"prefix": fname_prefix, "str_stamp": fname_stamp})

    is_wav = Path(file_path).suffix.upper() == ".WAV"

    if meta and is_wav:
        file_info.update(get_metadata(file_path))

    return file_info


def report_inv_stats(inv_df):
    """Generate a verbal summary of a file inventory.

    Issues a warning if all filenames in the inventory are not unique.

    Args:

        inv_df (pandas.DataFrame): Data frame containing basic information 
            about a set of files.

    Returns:

        str: Verbal summary of the inventory, including number of files, number
        of unique subfolders, total disk space used (GB), and total audio 
        duration (hours). 
    """

    extensions = set([Path(x).suffix for x in inv_df["name"]])
    ext_list_pretty = recite_list(extensions)

    n_files = len(inv_df)
    n_unique_filenames = len(pd.unique(inv_df["name"]))

    if n_unique_filenames < n_files:
        print("\nWARNING: Dataset contains duplicate filenames!")

    n_dirs = len(pd.unique(inv_df["dir"]))
    # n_serials = len(pd.unique(inv_df.serial)) if "serial" in inv_df.columns else None
    audio_h = sum(inv_df["duration"]) / 3600.
    data_gb = sum(inv_df["size"]) / 1024**3

    print(f"\nDirectory contains {n_files:,} {ext_list_pretty} files in {n_dirs} folders.")
    print(f"Total size: {data_gb:,.1f} GB.")
    print(f"Total duration: {audio_h:,.1f} h.")

    return



def summarize_inventory(inv_df, group_vars=["dir"], rel_path=True):
    """Aggregate information about files within a folder.

    Args:

        inv_df (pandas.DataFrame): Data frame containing detailed information
            about audio files in a folder, as produced by build_file_inventory.

        group_vars (list): List of variables on which to aggregate (summarize) 
            the inventory.

        rel_path (bool): Include only the relative path in the Folder output 
            column?

    Returns:

        pandas.DataFrame: Data frame summarizing values from the detailed 
        inventory.
    """

    top_dir = os.path.commonpath([str(i) for i in inv_df.dir])

    has_serial = "serial" in inv_df.columns

    inv_df["stamp_2"] = inv_df["stamp"]

    grouped_df = inv_df.groupby(group_vars)

    agg_functions = {"name": len,
                     "size": "sum",
                     "duration": "sum",
                     "stamp": "min",
                     "stamp_2": "max"}

    if has_serial:
        agg_functions.update({"serial": _summarize_serials})

    summary_df = grouped_df.aggregate(agg_functions)
    summary_df.reset_index(level=0, inplace=True)

    if rel_path:
        summary_df["Folder"] = [Path(i).relative_to(top_dir) for i in summary_df["dir"]]
    else:
        summary_df["Folder"] = summary_df["dir"]

    sum_out_cols = ["Folder", "Files", "Size_GB", "Duration_h", 
                    "Earliest", "Latest"]

    if has_serial:
        summary_df["Serial"] = summary_df["serial"]
        sum_out_cols.append("Serial")

    summary_df["Files"] = summary_df["name"]
    summary_df["Size_GB"] = [round(x / 1024**3, 1) for x in summary_df["size"]]
    summary_df["Duration_h"] = [round(x / 3600., 1) for x in summary_df["duration"]]
    summary_df["Earliest"] = [f"{x:%m/%d/%y}" for x in summary_df["stamp"]]
    summary_df["Latest"] = [f"{x:%m/%d/%y}" for x in summary_df["stamp_2"]]

    return summary_df[sum_out_cols]


