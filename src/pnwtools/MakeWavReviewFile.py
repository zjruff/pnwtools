"""
A script to generate a review_kscope style CSV file to allow us to look
at every part of a given set of wav files.

Arguments:

    target_dir (str): Path to the directory containing .wav files.
    
    clip_length (int): Duration of each clip in seconds. Optional; 
        default is 12 s.
    
    interval (int): Spacing of clips in seconds. Optional; default is 
        12 s. If interval is shorter than clip_length, successive clips
        will overlap.

Output:

    A CSV file listing short segments within an audio dataset, suitable
    for review and annotation using Wildlife Acoustics Kaleidoscope 
    software.

Usage:

    ``python MakeWavReviewFile.py [target_dir] [clip_length] [interval]``

"""

import os
import sys
from math import log10
from pnwtools import makeWavDict, makeWavLines


def main():
    target_dir = sys.argv[1]
    try:
        clip_length, interval = float(sys.argv[2]), float(sys.argv[3])
    except:
        clip_length, interval = 12, 12

    output_dir, output_name = os.path.split(target_dir)
    output_path = os.path.join(target_dir, "{0}_review_full.csv".format(output_name))

    header = "FOLDER,IN_FILE,CHANNEL,OFFSET,DURATION,PART,VOCALIZATIONS,MANUAL_ID"
    
    wavs = makeWavDict(target_dir)
    print("{0:,} .wav files found in target directory.".format(len(wavs)))

    outlines = [header]
    for x in sorted(wavs):
        outlines.extend(makeWavLines(wavs[x], target_dir, clip_length, interval))

    with open(output_path, 'w') as outfile:
        outfile.write('\n'.join(outlines))

    print("{0:,} lines written to {1}.".format(len(outlines) - 1, os.path.basename(output_path)))


if __name__ == "__main__":
    main()