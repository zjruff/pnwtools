"""
Script to create a CSV file summarizing .wav files in the directory at 
the recording station level.
"""

import os
import pnwtools
import sys


def main():
    try:
        target_dir = sys.argv[1]
    except:
        print("Please provide the path to the target directory.")
        exit()
    
    print("\nBuilding station info table... ", end='')
    
    dir_name = os.path.basename(target_dir)
    stn_info_path = os.path.join(target_dir, "{0}_station_info.csv".format(dir_name))
    
    stn_info = pnwtools.buildStationDict(target_dir)
    stn_info_lines = pnwtools.buildStationTable(stn_info)

    with open(stn_info_path, 'w') as stn_info_file:
        stn_info_file.write('\n'.join(stn_info_lines))
    
    print(" done.\n")
    
    os.startfile(stn_info_path, 'open')


if __name__ == "__main__":
    main()