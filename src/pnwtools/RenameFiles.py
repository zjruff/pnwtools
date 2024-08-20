"""Script to rename .wav files in a directory tree. Retains time and 
date info if present in the filename (e.g. wav files produced by 
Wildlife Acoustics ARUs). If not, generates a comparable timestamp 
based on when the file was last modified. Produces a table of stations
with first and last recording dates, amount of data, and ARU serial 
numbers if they are listed in the metadata.

"""

import os
import pnwtools
import sys
import wave


# For compatibility with Python 2 or 3
if hasattr(__builtins__, 'raw_input'):
    input = raw_input


def main():
    """
    If a log file already exists, script will ask user if they want 
    to undo any filename changes listed in the file. If yes, files will
    revert to their original names.
    """

    try:
        target_dir = sys.argv[1]
    except:
        print("Please provide the path to the target directory.")
        exit()

    rename_log_path = os.path.join(target_dir, "Rename_Log.csv")
    stn_info_path = os.path.join(target_dir, "Station_Info.csv")

    wavs = pnwtools.findWavs(target_dir)

    if os.path.exists(rename_log_path):
        print("It looks like files in this folder have already been renamed.")
        undo_cmd = input("Undo previous renaming operation? (y/n) ")
        if undo_cmd.lower() in ["yes", "y", "ok"]:
            pnwtools.undoRename(rename_log_path)
            os.remove(rename_log_path)
        else:
            pass
    else:
        print("Renaming {0} files... ".format(len(wavs))),
        log_lines = ["Old_path,New_path"]
        log_lines.extend(map(pnwtools.renameWav, wavs))
        
        with open(rename_log_path, 'w') as log_file:
            log_file.write('\n'.join(log_lines))
        
        print("done.")

    stn_info = pnwtools.buildStationDict(target_dir)
    stn_info_lines = pnwtools.buildStationTable(stn_info)

    with open(stn_info_path, 'w') as stn_info_file:
        stn_info_file.write('\n'.join(stn_info_lines))
    
    os.startfile(stn_info_path, 'open')


if __name__ == "__main__":
    main()