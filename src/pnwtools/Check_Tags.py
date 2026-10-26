"""
Script to tally up tags found in the MANUAL_ID column of a tagged
review_kscope file. Prints a human-readable summary of the review file,
including total number of lines, number of tagged lines, number of 
unique tags used, and a table showing counts of each tag broken up by
folder (e.g., recording station).

"""

import sys
from pnwtools.tagging import count_tags, summarize_tags


def main():
    try:
        target_file = sys.argv[1]
    except:
        print("Please provide the path to the target file.")
        exit()

    tag_info = count_tags(target_file)
    summarize_tags(tag_info)

    exit()


if __name__ == "__main__":
    main()
