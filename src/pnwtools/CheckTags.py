"""
Script to tally up tags found in the MANUAL_ID column of a tagged
review_kscope file. Prints a human-readable summary of the review file,
including total number of lines, number of tagged lines, number of 
unique tags used, and a table showing counts of each tag broken up by
folder (e.g., recording station).

"""

import sys
from pnwtools import countTags, summarizeTags


def main():
    try:
        target_file = sys.argv[1]
    except:
        print("Please provide the path to the target file.")
        exit()

    tag_info = countTags(target_file)
    summarizeTags(tag_info)

    exit()


if __name__ == "__main__":
    main()
