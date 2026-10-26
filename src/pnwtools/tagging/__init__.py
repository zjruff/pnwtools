"""
`pnwtools.tagging`

Defines functions for creating and summarizing review files.

Functions:

    count_tags
        Tally user-applied ID tags in a tagged Kaleidoscope review file.

    build_blank_kscope_table
        Build a blank Kaleidoscope review file for all WAV files in a folder.

    summarize_tags
        Print a summary of user-applied ID tags in a review file.
"""

import os
import re
import sys
import pandas as pd
from pathlib import Path
from pnwtools.utils.file import find_files
from pnwtools.utils.audio import segment_audio


def count_tags(tagged_file_path):
    """Tally user-applied ID tags in a tagged review file.

    Args:

        tagged_file_path (pathlib.Path or str): Path to a Kaleidoscope-
            formatted review file containing user-applied ID tags.

    Returns:

        dict: Dictionary containing two dictionaries: file_info, which
        lists the path, filename, modification time, total lines, 
        number of tagged lines, and the number of unique tags used; and
        tag_counts, indexed by tag and by folder (from the FOLDER field
        of the review file), listing the number of instances of each 
        unique tag.
    """

    with open(tagged_file_path) as tagged_file:
        lines = [line.replace('"', '').rstrip() for line in tagged_file.readlines()]

    headers = [x.replace(' ', '_').replace('*', '').upper() for x in lines[0].split(',')]
    n_fields = len(headers)
    n_lines = len(lines) - 1
    n_tagged_lines = 0
    tag_counts = {}

    try:
        manid_field = headers.index("MANUAL_ID")
        infile_field = headers.index("IN_FILE")
        folder_field = headers.index("FOLDER")
    except:
        print("Required fields were not found in the file specified.")
        return

    folders = list(set([line.split(',')[folder_field] for line in lines[1:]]))

    for line in lines[1:]:
        vals = line.split(',')
        n_vals = len(vals)

        filename, folder = vals[infile_field], vals[folder_field]
        if folder == '':
            folder = "NA"

        n_comma_tags = n_vals - n_fields
        labels = '+'.join(vals[manid_field : manid_field + n_comma_tags + 1])

        if labels != '':
            n_tagged_lines += 1
            tags = labels.split('+')
            for tag in tags:
                if not tag in tag_counts:
                    tag_counts[tag] = dict(zip(folders, [0 for i in folders]))
                tag_counts[tag][folder] += 1

    file_info = {
        "file_path": tagged_file_path,
        "file_name": os.path.basename(tagged_file_path),
        "file_mtime": os.path.getmtime(tagged_file_path), 
        "total_lines": n_lines,
        "tagged_lines": n_tagged_lines,
        "unique_folders": sorted(folders),
        "unique_tags": len(tag_counts)
        }

    results = {"file_info": file_info, "tag_counts": tag_counts}

    return results


def build_blank_kscope_table(top_dir, **segment_params):
    """Build a blank Kaleidoscope review file for all WAV files in a folder.

    If interval is not specified it will be set equal to seg_dur, producing 
    non-overlapping segments. If interval < seg_dur, successive segments will 
    overlap. If interval > seg_dur, there will be gaps between segments. 

    Args:

        top_dir (pathlib.Path or str): Path to the root of the directory tree
            containing the WAV files.

        segment_params: Optional keyword arguments to be passed to 
            pnwtools.utils.audio.segment_audio.
    """

    wavs = find_files(top_dir, "wav")

    wav_dfs = []
    for w in wavs:
        try:
            w_offs, w_durs = zip(*segment_audio(w, **segment_params))
            n_segments = len(w_offs)

            w_rel_dir = '' if w.parent == Path(top_dir) else str(w.parent.relative_to(top_dir))

            w_df = pd.DataFrame({"OFFSET": w_offs,
                                 "DURATION": w_durs})
            w_df["FOLDER"] = w_rel_dir
            w_df["IN_FILE"] = w.name
            w_df["CHANNEL"] = 1
            w_df["VOCALIZATIONS"] = 1
            w_df["MANUAL_ID"] = ''

            wav_dfs.append(w_df)
        except:
            continue

    out_cols = ["FOLDER", "IN_FILE", "CHANNEL", "OFFSET", "DURATION", 
                "VOCALIZATIONS", "MANUAL_ID"]

    kscope_table = pd.concat(wav_dfs, axis=0)[out_cols]

    return kscope_table


def summarize_tags(tag_count_dict):
    """Print a summary of user-applied ID tags in a review file.

    Args:

        count_dict (dict): Dictionary produced by countTags function.

    Returns:

        Nothing.
    """

    finfo = tag_count_dict["file_info"]
    tag_counts = tag_count_dict["tag_counts"]
    folders = finfo["unique_folders"]

    str_mtime = datetime.fromtimestamp(finfo["file_mtime"]).strftime("%b %d at %H:%M")

    print("\nFile {0} was last saved {1}.".format(finfo["file_name"], str_mtime))
    print("{0:,} of {1:,} lines are tagged.\n".format(finfo["tagged_lines"], finfo["total_lines"]))

    if finfo["tagged_lines"] > 0:
        print("{0} unique tags were used:\n".format(finfo["unique_tags"]))
        print("Tag\t\t{0}".format('\t\t'.join(folders)))
        for label in sorted(tag_counts, key = lambda x: ("?" in x, x)):
            counts = '\t\t'.join([str(tag_counts[label][f]) for f in folders])
            print("{0}\t\t{1}".format(label, counts))
        print("")

    return


