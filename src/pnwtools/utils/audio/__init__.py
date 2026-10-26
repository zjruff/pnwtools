"""
`pnwtools.utils.audio`

Defines functions for handling audio files.

Functions:

    check_wav_file
        Get basic information about a WAV file using `wave`.

    check_sound_file
        Get basic information about an audio file using `soundfile`.

    check_audio_file
        Get information about an audio file based on its file extension.

    extract_wav_segment
        Create a new WAV file from a segment of an existing WAV file.

    segment_audio
        Subdivide an audio file into a number of segments of fixed length.
"""

import os
import soundfile as sf
import wave
from datetime import datetime
from pathlib import Path
from ..file import get_file_info
from ..lists import number_items
from ..naming import add_suffix


def check_wav_file(file_path):
    """Get basic information about a WAV file.

    Args:

        file_path: Path to the .wav file.

    Returns:

        dict: Dictionary of basic information about the wav file.
    """

    wav_info = get_file_info(file_path)

    try:
        f = wave.open(str(file_path))
        w_vals = f.getparams()
        f.close()
        w_fr, w_frames, w_channels = w_vals.framerate, w_vals.nframes, w_vals.nchannels
        w_dur = w_frames / w_fr
        err = False
    except:
        w_fr, w_frames, w_channels, w_dur = 0, 0, 0, 0
        err = True

    wav_info.update({'channels': w_channels,
                     'framerate': w_fr,
                     'n_frames': w_frames,
                     'duration': w_dur,
                     'error': err})

    return wav_info


def check_sound_file(file_path):
    """Get basic information about an audio file.

    This is identical to `check_wav_file` but relies on the third-party
    `soundfile` package rather than the `wave` module from the Python standard
    library, so it can handle any audio format that `soundfile` supports. 
    If you only have WAV files, `check_wav_file` is faster.

    Args:

        file_path: Path to the audio file.

    Returns:

        dict: Dictionary of basic information about the audio file.
    """

    file_info = get_file_info(file_path)

    try:
        with sf.SoundFile(file_path) as f:
            a_frames = f.frames
            a_fr = f.samplerate
            a_channels = f.channels
        a_dur = a_frames / a_fr
        err = False
    except:
        a_frames, a_fr, a_channels, a_dur = 0, 0, 0, 0
        err = True

    file_info.update({'channels': a_channels,
                      'framerate': a_fr,
                      'n_frames': a_frames,
                      'duration': a_dur,
                      'error': err})

    return file_info


def check_audio_file(file_path):
    """Get information about an audio file based on its file extension.

    If the file has a .wav extension, it is checked using check_wav_file; 
    otherwise, it is checked using check_sound_file.

    Args:

        file_path: Path to the audio file.

    Returns:

        dict: Dictionary of basic information about the audio file.
    """

    if Path(file_path).suffix.upper() == ".WAV":
        file_info = check_wav_file(file_path)
    else:
        file_info = check_sound_file(file_path)

    return file_info


def extract_wav_segment(src_path, dst_path, start_s, dur_s):
    """Create a new WAV file from a segment of an existing WAV file.

    Args:

        src_path (str or pathlib.Path): Path to the source .wav file.

        dst_path (str): Path to the new .wav file that will be created
            (or overwritten if it already exists).

        start_s (numeric): Offset in seconds from the start of the source file
            to the start of the segment.

        dur_s (numeric): Duration of the portion of the source .wav file to be
            copied.

    Returns:

        int: Number of samples written to the new file, or -1 if the source
        file could not be read.
    """

    try:
        src_info = check_wav_file(src_path)
        if src_info["error"]:
            raise ValueError("Source file could not be read.")
        else:
            src_dur = src_info['duration']
            src_fr = src_info['framerate']
            src_frames = src_info['n_frames']

        if start_s > src_dur:
            raise ValueError("Starting offset exceeds source file duration.")
        else:
            start_frame = start_s * src_fr

        target_frames = int(dur_s * src_fr)
        seg_frames = min(src_frames - start_frame, target_frames)

        src_wav = wave.open(str(src_path), mode='rb')
        src_params = src_wav.getparams()
        dst_wav = wave.open(dst_path, mode='wb')
        dst_wav.setparams(src_params)
        dst_wav.setnframes(seg_frames)
        src_wav.setpos(start_frame)
        dst_wav.writeframes(src_wav.readframes(seg_frames))

        src_wav.close()
        dst_wav.close()

        return seg_frames
    except:
        return -1


def segment_audio(file_path, seg_dur, interval=None, min_seg_dur=None):
    """Subdivide an audio file into a number of segments of fixed length.

    If interval is not specified it will be set equal to seg_dur, producing 
    non-overlapping segments. If interval < seg_dur, successive segments will 
    overlap. If interval > seg_dur, there will be gaps between segments. If
    min_seg_dur is specified, segments with duration less than this value 
    (e.g., at the end of the file) will be omitted from the list. For very 
    short files this may yield an empty list.

    Args:

        file_path (pathlib.Path or str): Path to the audio file.

        seg_dur (numeric): Desired length of each segment, in seconds.

        interval (numeric): Interval in seconds from the start of a segment to 
            the start of the next segment.

        min_seg_dur (numeric): Minimum allowable segment length in seconds.

    Returns:

        list: List of tuples representing the start position (offset) and 
        duration of each segment in seconds.
    """

    file_dur = check_audio_file(file_path)['duration']

    if not interval:
        interval = seg_dur

    # Don't want to deal with a bunch of weird edge cases if we let this be 0
    if not min_seg_dur:
        min_seg_dur = 0.01

    n_segments = int(file_dur // interval) + int(file_dur % interval != 0)  
    clip_indices = [i*interval for i in range(n_segments)]
    clip_durs = [min(seg_dur, file_dur-j) for j in clip_indices]
    
    clip_info = [k for k in zip(clip_indices, clip_durs) if k[1] >= min_seg_dur]

    return clip_info
