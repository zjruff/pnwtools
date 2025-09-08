"""08 Sep 2025

RecoverFilenames.py

Script to try and recover the names of .wav files based on WA and/or
Guano-formatted metadata and/or recording date.
If the user supplies a prefix, that will be applied to any files 
recovered in this way. Otherwise, the ARU serial number will be used as
a prefix.
"""

from datetime import datetime
import os
import pnwtools
import re
import sys
from glob import glob
from pathlib import Path


# For compatibility with Python 2
if hasattr(__builtins__, 'raw_input'):
    input = raw_input


def main():
    try:
        top_dir = sys.argv[1]
    except:
        print("\nNo target directory provided.\n")
        exit()
    
    try:
        use_prefix = sys.argv[2]
    except:
        use_prefix = None


    wavs = pnwtools.findWavs(top_dir)
    to_recover = [x for x in wavs if Path(x).name[:4] == "File"]

    print("Attempting to rename {0} files.".format(len(to_recover)))

    n_fixed, n_err = 0, 0
    log_lines = []

    for fpath in to_recover:
        f = Path(fpath)
        fdir, fname = f.parent, f.name
        parent = fdir.name

        try:
            serial = pnwtools.getSerial(fpath)
            stamp = pnwtools.getTimestampFromMetadata(fpath)
            str_stamp = stamp.strftime("%Y%m%d_%H%M%S")

            if use_prefix is not None:
                prefix = use_prefix
            else:
                prefix = serial

            newfname = "{0}_{1}.wav".format(prefix, str_stamp)
            newfpath = os.path.join(fdir, newfname)

            os.rename(fpath, newfpath)
            
            log_lines.append("{0},{1}".format(fname, newfname))
            n_fixed += 1
        except:
            log_lines.append("{0},NA".format(fname))
            n_err += 1


    print("{0} files renamed successfully.\n".format(n_fixed))
    if n_err > 0:
        print("Failed to retrieve metadata for {0} files.".format(n_err))

    with open(os.path.join(top_dir, "Rename_Log.csv"), 'w') as logfile:
        logfile.write("Old_name,New_name\n")
        logfile.write('\n'.join(log_lines))


if __name__ == '__main__':
    main()