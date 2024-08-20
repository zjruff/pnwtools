# pnwtools

`pnwtools` is a collection of software tools intended to be useful for
researchers and technicians with the USDA Forest Service Pacific 
Northwest Research Station, specifically those involved in passive 
acoustic monitoring of Northern spotted owls and other forest wildlife.
These tools may also be useful to others doing bioacoustics work but
please note that they are mostly designed for use within the USFS 
spotted owl monitoring program and will reflect its various 
idiosyncrasies.

`pnwtools` is structured as a Python package for ease of distribution 
via [the Python Package Index (PyPI.org)](https://pypi.org/project/pnwtools/)
but mostly consists of a collection of scripts that can be run as 
standalone command-line tools. See the Scripts section below for notes 
on the available scripts and how to use them.

This package is intended to be a living collection and will be updated 
periodically with new scripts and improvements to existing scripts. If 
there are tools or features you would like to see added, please email 
Zack via zjruff at gmail dot com.

## Installation

**Note: As of 8/20 the package is NOT YET available from PyPI.org. 
Just getting the repository set up at the moment.**

`pnwtools` is compatible with all modern versions of Python (2.7 and 
3+) and can be installed using `pip` like so:

```
python -m pip install pnwtools
```

Note that there is an unrelated package called `pwntools` which 
provides tools for Capture The Flag-style cybersecurity competitions. 
The similar spelling makes it very easy to install this other package 
by mistake, so we recommend simply copying and pasting the above 
command into your shell program.

To make sure you are using the latest available version of `pnwtools`,
you can update it at any time like so:

```
python -m pip install --upgrade pnwtools
```

This will search PyPI for a version of `pnwtools` that's newer than the
one you have installed; if there is a newer version available, pip will 
install it for you.

## Scripts
These scripts are provided as standalone command-line tools that can be
run from a shell program such as Windows PowerShell, Bash, the Anaconda
Prompt, Konsole, etc. etc. If you installed pnwtools in a conda 
environment, you will need to activate the environment before running
these scripts.

### `rename_files`

This script will standardize the names of .wav files within the target 
directory tree. The standardized name of each file will consist of a 
prefix and a timestamp. The prefix will be generated based on the two 
lowest-level path components of the directory containing the file, i.e.
the file's parent directory and that directory's parent directory. 
If the filename already contains a timestamp in the expected format 
(YYYYMMDD_HHMMSS, as used by Wildlife Acoustics ARUs), it will be 
preserved. If not, the timestamp will be generated from each .wav 
file's last modification time.

Run this script like so:

```
rename_files D:\Path\to\target_dir
```

### `station_info`

This script will create a table summarizing the .wav files in the 
target directory by recording station. The summary will be written to
a CSV file listing the station ID, number of valid .wav files, first
and last recording dates, and the serial number of the ARU (or "NA" if
the serial number could not be read).

Run this script like so:

```
station_info D:\Path\to\target_dir
```

### `check_tags`

This script will summarize the ID tags that have been applied to a 
review file. The review file must have columns named FOLDER, IN_FILE,
and MANUAL_ID and any tags to be counted must be present in the 
MANUAL_ID column. The output will include a summary of the review file,
including when it was last saved, the total number of lines, the number 
of tagged lines, and the number of unique tags used. The script will 
print a summary of the tags used and how many times each tag occurs in
each FOLDER (e.g. recording station).

Run this script like so:

```
check_tags D:\Path\to\Site_Name\Site_Name_review_kscope.csv
```

### `make_wav_review_file`

This script will create a CSV file listing all .wav files in the target
directory, with each audio file split into short segments for manual 
review. There are two optional arguments, `clip_length` and `interval`.
`clip_length` indicates the desired length (in seconds) of the segments
into which each audio file will be divided. `interval` indicates the 
interval (also in seconds) between the start of one segment and the 
start of the next segment. By default these are both 12 s, meaning the
audio will be divided into non-overlapping 12-s segments.

To run this script with the default behavior, run

```
make_wav_review_file D:\Path\to\target_dir
```

To run the script using different values for `clip_length` and 
`interval`, run

```
make_wav_review_file D:\Path\to\target_dir 12 8
```
