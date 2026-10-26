"""
`pnwtools.utils.metadata`

Defines functions and classes for dealing with Wildlife Acoustics WAMD and 
GUANO metadata.

This module borrows heavily from the `guano-py` codebase maintained by David 
Riggs and others, available at https://github.com/riggsd/guano-py
The code reproduced here adds functionality that is not 
currently part of the guano API.

Functions:

    get_metadata
        Extract ARU serial number and timestamp from WAV file metadata.

    read_wamd
        Read [Wildlife Acoustics] WAMD metadata from a WAV file.

Classes:

    RiffChunk
        Class to replicate the functionality of the `Chunk` class from the 
        now-deprecated `chunk` module when running Python 3.13 or greater. 
"""

import os
import re
import struct
import sys
import warnings
import wave
from datetime import datetime, timedelta
from guano import GuanoFile, tzoffset
from pathlib import Path


CHUNK_AVAIL = True if sys.version_info.minor < 13 else False
if CHUNK_AVAIL:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import chunk


def get_metadata(file_path):
    """Extract WAV file metadata in either WAMD or Guano format.

    Look for WAMD metadata first, then try GUANO. If neither option produces 
    usable values, the returned values will be an empty string ('') or None.

    Args:

        file_path (pathlib.Path or str): Path to a WAV file.

    Returns:

        str: Dictionary listing metadata values 
    """

    file_dir, filename = Path(file_path).parent, Path(file_path).name

    try:
        wamd = read_wamd(file_path)
        serial = wamd.get("serial", "")
        model = wamd.get("model", "")
        str_stamp = wamd.get("timestamp", None)
    except:
        try:
            gf = GuanoFile(file_path)
            serial = gf.get("Serial", "")
            model = gf.get("Model", "")
            str_stamp = gf.get("Timestamp", None)
        except:
            serial, model, str_stamp = "", "", None
    if str_stamp:
        stamp = _parse_wamd_timestamp(str_stamp)
    else:
        stamp = None

    md_dict = {"dir": file_dir, 
               "name": filename, 
               "serial": serial, 
               "model": model, 
               "stamp": stamp}

    return md_dict


# binary WAMD field identifiers
WAMD_IDS = {
    0x00: 'version',
    0x01: 'model',
    0x02: 'serial',
    0x03: 'firmware',
    0x05: 'timestamp',
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
    'gpsfirst': lambda x: _parse_wamd_gps(x)
}


def _parse_text(value):
    """Coerce text to UTF-8 encoding."""
    return value.decode('utf-8')


def _parse_wamd_timestamp(timestamp):
    """WAMD timestamps are one of these known formats:

    2014-04-02 22:59:14-05:00

    2014-04-02 22:59:14.000

    2014-04-02 22:59:14

    Produces a `datetime.datetime`.

    """
    if isinstance(timestamp, bytes):
        timestamp = timestamp.decode('utf-8')
    if len(timestamp) == 25:
        dt, offset = timestamp[:-6], timestamp[19:]
        tz = tzoffset(offset)
        return datetime.strptime(dt, '%Y-%m-%d %H:%M:%S').replace(tzinfo=tz)
    elif len(timestamp) == 23:
        return datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
    elif len(timestamp) == 19:
        return datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    else:
        return None


def _read_chunk(target, chunk_avail=CHUNK_AVAIL):
    """Read input using chunk.Chunk if available, or with RiffChunk if not."""
    
    if chunk_avail:
        target_chunk = chunk.Chunk(target, bigendian=False)
    else:
        target_chunk = RiffChunk(target)

    return target_chunk


# This class definition is copied directly from the wamd2guano.py 
# utility script in the guano package.
class RiffChunk:
    """A replacement for chunk.Chunk to handle RIFF chunks."""

    def __init__(self, file_or_chunk, bigendian=False):
        self.bigendian = bigendian
        self.format = '>I' if bigendian else '<I'

        # Determine if we're reading from a file or another chunk
        if isinstance(file_or_chunk, RiffChunk):  # It's a parent chunk
            self.parent = file_or_chunk
            self.file = self.parent.file
        else:  # It's a file
            self.file = file_or_chunk
            self.parent = None

        # Read chunk header
        if self.parent:
            self.name = self.parent.read(4)
        else:
            self.name = self.file.read(4)

        if len(self.name) < 4:
            raise EOFError

        # Read chunk size
        if self.parent:
            size_bytes = self.parent.read(4)
        else:
            size_bytes = self.file.read(4)

        if len(size_bytes) < 4:
            raise EOFError

        self.size = struct.unpack(self.format, size_bytes)[0]
        self.bytes_read = 0

    def getname(self):
        """Return the name (ID) of this chunk."""
        return self.name

    def getsize(self):
        """Return the size of this chunk's data."""
        return self.size

    def read(self, size=None):
        """Read at most size bytes from this chunk."""
        if size is None:
            size = self.size - self.bytes_read
        else:
            size = min(size, self.size - self.bytes_read)

        if size <= 0:
            return b''

        data = self.file.read(size)
        self.bytes_read += len(data)

        # If we have a parent, update its bytes_read too
        if self.parent:
            self.parent.bytes_read += len(data)

        return data

    def skip(self):
        """Skip to the end of this chunk."""
        if self.bytes_read < self.size:
            remaining = self.size - self.bytes_read

            if self.parent:
                # For nested chunks, we need to read (and discard) the data
                # instead of seeking, so parent's position is updated correctly
                self.read(remaining)
            else:
                # Direct file access can use seek
                self.file.seek(remaining, 1)
                self.bytes_read = self.size

        # Handle alignment - chunks are word-aligned
        if self.size % 2:
            if self.parent:
                self.parent.read(1)  # Read and discard padding byte
            else:
                self.file.seek(1, 1)
                # No need to update bytes_read for padding


def read_wamd(file_path):
    """Extract WAMD metadata from a .WAV file as a dict."""
    with open(file_path, 'rb') as f:
        # Check the first chunk to make sure this is a wave file
        # ch = chunk.Chunk(f, bigendian=False)
        # ch = RiffChunk(f)
        ch = _read_chunk(f)
        if ch.getname() != b'RIFF':
            raise Exception(f"{Path(file_path).name} is not a RIFF file!")
        if ch.read(4) != b'WAVE':
            raise Exception(f"{Path(file_path).name} is not a WAVE file!")

        # Look for a chunk called 'wamd' which contains the WAMD metadata
        wamd_chunk = None
        while True:
            try:
                # subch = chunk.Chunk(ch, bigendian=False)
                # subch = RiffChunk(ch)
                subch = _read_chunk(ch)
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


