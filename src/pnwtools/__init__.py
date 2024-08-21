"""`pnwtools` package for working with bioacoustics data

The functions defined herein are not really intended as a complete 
functional API; rather, they form the bones of a number of utility 
scripts which are the main point of the package. However, the 
functions themselves may also be useful, so they are collected here 
for ease of discovery.

:copyright: (c) 2024 by Zachary J. Ruff
:license: GNU General Public License v3; see LICENSE for details.
"""

import chunk
import os
import re
import struct
import wave
from datetime import datetime, timedelta
from guano import GuanoFile


################################################################################
########### Miscellaneous functions for dealing with .wav files ################

def findWavs(top_dir):
    """Get a sorted list of .wav files within a directory tree."""
    wavs = []
    for root, dirs, files in os.walk(top_dir):
        for file in files:
            if file[-4:].lower() == ".wav":
                wavs.append(os.path.join(root, file))
    return sorted(wavs)


def makeWavDict(top_dir):
    """Create a dictionary of .wav file paths indexed by filename."""
    wav_paths = findWavs(top_dir)
    
    wav_dict = dict(zip([os.path.basename(x) for x in wav_paths], wav_paths))
    
    return wav_dict


def getStamp(wav_path):
    """Get the timestamp of a .wav file.
    
    If the filename contains a readable timestamp in YYYYMMDD_HHMMSS 
    format, that timestamp will be preserved. Otherwise, the timestamp
    will be the .wav file's last modification time.
    
    """
    str_stamp = '_'.join(wav_path.split('_')[-2:])
    try:
        stamp = datetime.strptime(str_stamp, "%Y%m%d_%H%M%S.wav")
    except:
        wav_mtime = os.path.getmtime(wav_path)
        stamp = datetime.fromtimestamp(wav_mtime)
    return stamp


def getStn(wav_path):
    """Construct an area_hex-stn identifier from the directory path."""
    wav_dir = os.path.dirname(wav_path)
    hex_dir, stn_dir = wav_dir.split(os.sep)[-2:]
    stn_id = stn_dir.split('_')[-1]
    stn = "{0}-{1}".format(hex_dir, stn_id)
    return stn


def getWavLength(wav_path):
    """Calculate the duration of a .wav file in seconds."""
    try:
        w = wave.open(wav_path)
        n_samples, sample_rate = w.getnframes(), w.getframerate()
        w.close()
        wav_length = float(n_samples) / sample_rate
    except:
        wav_length = 0
    return wav_length


def checkWav(wav_path):
    """Check to make sure wav_path is a valid wav file."""
    if os.path.getsize(wav_path) == 262144:
        valid = False
    else:
        try:
            with open(wav_path, 'rb') as f:
                ch = chunk.Chunk(f, bigendian=False)
                if ch.getname() != b'RIFF':
                    valid = False
                elif ch.read(4) != b'WAVE':
                    valid = False
                else:
                    valid = True
        except:
            valid = False
    return valid


def checkWavFilename(filename, folder):
    """Check that a .wav filename matches preferred formatting.
    
    Preferred format is [Area]_[Hex ID]-[Stn ID]_YYYYMMDD_HHMMSS.wav.
    """
    filename_patt = re.compile("[A-Z]{3,5}_[0-9]{5}-[A-Z0-9]+?_[0-9]{8}_[0-9]{6}.wav")
    if filename_patt.match(filename):
        hex_dir, stn_dir = folder.split('/')[-2:]
        stn_id = stn_dir.split('_')[-1]
        prefix = "{0}-{1}".format(hex_dir, stn_id)
        if filename[:len(prefix)] == prefix:
            return True
    else:
        return False


def makeWavLines(wav_path, target_dir, clip_length, interval):
    """Create a table listing short segments of a wav file for review.
    
    Setting `interval` to less than `clip_length` allows segments to
    overlap, which can be useful.
    
    """
    fdir, fname = os.path.split(wav_path)
    folder = fdir.replace(target_dir + os.sep, "")
    wav_length = pnwtools.getWavLength(wav_path)
    if wav_length == 0:
        output_lines = []
    else:
        n_part_digits = int(log10(wav_length / interval)) + 1
        n_pos_digits = int(log10(wav_length)) + 1
        output_lines = []
        i = 1
        while True:
            offs = (i - 1) * interval
            if clip_length == interval:
                str_part = "part_%s" % str(i).zfill(n_part_digits)
            else:
                str_part = "pos_%s" % str(int(offs)).zfill(n_pos_digits)
            
            if offs + clip_length < wav_length:
                dur = clip_length
            else:
                dur = wav_length - offs
                if dur < clip_length:
                    break
            
            new_line = "{0},{1},0,{2},{3},{4},1,".format(folder, fname, offs, dur, str_part)
            output_lines.append(new_line)
            i = i + 1

    return output_lines

################################################################################
############## Functions for renaming a set of .wav files ######################

def renameWav(old_path):
    """Intelligently rename a .wav file.
    
    Infers the hex ID and station from the two lowest level directories
    in the file's path, e.g. if the file is in F:\Data\OLY_30020\Stn_1 
    the original prefix will be replaced with "OLY_30020-1."
    Only retains timestamp information from original filename, i.e. the
    last two components when the name is split by '_'.
    Replaces $ with _ to deal with weird filenames that ARUs sometimes 
    spit out when the recording quality is wonky.
    """
    
    wav_dir, old_name = os.path.split(old_path)
    old_name = old_name.replace('$', '_')
    
    hex_id, stn_dir = wav_dir.split(os.sep)[-2:]
    stn_id = stn_dir.split('_')[-1]
    
    str_stamp = '_'.join(old_name.split('_')[-2:])
    
    new_name = "{0}-{1}_{2}".format(hex_id, stn_id, str_stamp)
    new_path = os.path.join(wav_dir, new_name)

    if new_path != old_path:
        os.rename(old_path, new_path)
    else:
        pass

    return "{0},{1},{2}".format(wav_dir, old_name, new_name)


def undoRename(log_path):
    """Undo a renaming operation based on an existing log file."""
    
    with open(log_path) as log_file:
        log_lines = log_file.readlines()[1:]
        print("Reverting {0} filenames... ".format(len(log_lines))),
    
    for line in log_lines:
        wav_dir, old_name, new_name = line.rstrip().split(',')
        old_path, new_path = os.path.join(wav_dir, old_name), os.path.join(wav_dir, new_name)

        if old_path == new_path:
            continue
        else:
            os.rename(new_path, old_path)
    
    print("done.")


################################################################################
############# Functions for summarizing a set of .wav files ####################

def buildStationDict(top_dir):
    """Build a dictionary of info about .wav files in a directory."""
    
    wavs = findWavs(top_dir)
    good_wavs = list(filter(checkWav, wavs))
    stns = sorted(list(set(map(getStn, good_wavs))))

    stn_dict = dict(zip(stns, [{'dates':[], 'serials':[], 'n_wavs':0} for i in stns]))

    for wav in good_wavs:
        stn, stamp = getStn(wav), getStamp(wav)
        stn_dict[stn]['dates'].append(stamp)
        stn_dict[stn]['n_wavs'] += 1
        try:
            serial = getSerial(wav)
            stn_dict[stn]['serials'].append(serial)
        except:
            pass

    return stn_dict


def buildStationTable(stn_dict):
    """Summarize info on .wavs in a directory tree in table form."""

    stn_info_lines = ["Station ID,Valid wavs,Earliest,Latest,Serial number"]
    
    stns = sorted(stn_dict.keys())

    for stn in stns:
        stn_dates = stn_dict[stn]['dates']
        good_dates = list(filter(lambda d: d.year >= 2017, stn_dates))
        first_date, last_date = min(good_dates), max(good_dates)
        str_first = first_date.strftime("%m/%d/%y")
        str_last = last_date.strftime("%m/%d/%y")
        serials = '+'.join(list(set(stn_dict[stn]['serials'])))
        n_wavs = stn_dict[stn]['n_wavs']
        stn_info_lines.append("{0},{1},{2},{3},{4}".format(stn, n_wavs, str_first, str_last, serials))

    return stn_info_lines


################################################################################
############# Functions for dealing with tagged review files ####################

def countTags(tagged_file_path):
    """Tally user-applied ID tags in a tagged review file.

    Args:

        tagged_file_path (str): Path to a review file containing user-
            applied ID tags.

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


def summarizeTags(tag_count_dict):
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


################################################################################
########## Functions for dealing with .wav metadata (WAMD and GUANO) ###########

# The complicated stuff is lifted from the `wamd2guano` script that is 
# included in the `guano` package.

# binary WAMD field identifiers
WAMD_IDS = {
    0x00: 'version',
    0x01: 'model',
    0x02: 'serial'
}

# fields that we exclude from our in-memory representation
WAMD_DROP_IDS = (
    0x0D,    # voice note embedded .WAV
    0x10,    # program binary
    0x11,    # runstate giant binary blob
    0xFFFF  # used for 16-bit alignment 
)

# rules to coerce values from binary string to native types (default is `str`)
WAMD_COERCE = {
    'version': lambda x: struct.unpack('<H', x)[0],
    'gpsfirst': lambda x: _parse_wamd_gps(x),
    'time_expansion': lambda x: struct.unpack('<H', x)[0] 
}


def _parse_text(value):
    """Coerce text to UTF-8 encoding."""
    return value.decode('utf-8')


def wamd(fname):
    """Extract WAMD metadata from a .WAV file as a dict."""
    with open(fname, 'rb') as f:
        # Just checking the first chunk to make sure this is a wave file
        ch = chunk.Chunk(f, bigendian=False)
        if ch.getname() != b'RIFF':
            raise Exception('%s is not a RIFF file!' % fname)
        if ch.read(4) != b'WAVE':
            raise Exception('%s is not a WAVE file!' % fname)

        # Look for a chunk called 'wamd' which contains the WAMD metadata
        wamd_chunk = None
        while True:
            try:
                subch = chunk.Chunk(ch, bigendian=False)
            except EOFError:
                break
            if subch.getname() == b'wamd':
                wamd_chunk = subch
                break
            else:
                subch.skip()
        if not wamd_chunk:
            raise Exception('"wamd" WAV chunk not found in file %s' % fname)

        metadata = {}
        offset = 0
        size = wamd_chunk.getsize()
        buf = wamd_chunk.read(size)
        while offset < size:
            id = struct.unpack_from('< H', buf, offset)[0]
            len = struct.unpack_from('< I', buf, offset+2)[0]
            val = struct.unpack_from('< %ds' % len, buf, offset+6)[0]
            if id not in WAMD_DROP_IDS:
                name = WAMD_IDS.get(id, id) # Return id if it isn't a valid key
                val = WAMD_COERCE.get(name, _parse_text)(val)
                metadata[name] = val
            offset += 6 + len
        return metadata


def getSerial(fpath):
    """Get the ARU serial number from .wav metadata, if available.
    
    Look for WAMD metadata first, then try GUANO. If neither option 
    produces a usable value, the serial number is returned as "NA".
    """
    
    try:
        serial = wamd(fpath)["serial"]
    except:
        try:
            gf = GuanoFile(fpath)
            serial = gf["Serial"]
        except:
            serial = "NA"
    return serial
