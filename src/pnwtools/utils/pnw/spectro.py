"""
pnwtools.utils.pnw.spectro

Functions specifically for generating spectrograms using SoX with parameters
tailored for processing using PNW-Cnet.

Functions:

    build_spectro_command
        Generate a command formatted for execution by SoX to generate a 
        spectrogram image file from a segment of an audio file.

    build_spectrogram_table
        Get information on spectrograms to be generated from an audio file.

    generate_spectrogram
        Generate a command to create a spectrogram and execute it with SoX. 

    get_spectro_info
        Get information on spectrograms to be generated from one audio file.

    prep_spectro_gen
        Generate a set of commands to create spectrograms representing segments 
        of a set of audio files. 
"""

import os
from pathlib import Path
from pnwtools.utils.audio import segment_audio
from pnwtools.utils.file import find_files
from pnwtools.utils.lists import flatten_list, number_items, split_list
from pnwtools.utils.naming import add_suffix


def build_spectro_command(src_path, offset, duration, dst_path):
    """Format a set of spectrogram generation parameters as a call to SoX.

    Spectrogram parameters (e.g. dimensions and dynamic range) are hardcoded 
    as part of the canonical audio preprocessing procedure for PNW-Cnet. 
    Specifically, the call to SoX will isolate Channel 1 of the audio, resample
    it to 8 kHz, 

    Args:

        src_path (str): Path to the source file.

        offset (numeric): Starting offset for the portion of the source file 
            from which the spectrogram will be generated.

        duration (numeric): Duration of the audio segment from which the 
            spectrogram will be generated.

        dst_path (str): Path to the image file that will be created.

    Returns:

        str: A command that can be passed to SoX to generate a spectrogram.
    """

    spectro_params = "remix 1 rate 8k spectrogram -x 1000 -y 257 -z 90 -m -r"

    spectro_command = f'sox "{src_path}" -V1 -n trim {offset} {duration} {spectro_params} -o "{dst_path}"'

    return spectro_command


def generate_spectrogram(spectro_params, sox_path="sox"):
    """Generate a single spectrogram using SoX.

    Args:

        spectro_params (tuple): A tuple including the path to the source file,
            the offset within the source file in seconds, the duration of the
            audio segment in seconds, and the path to the spectrogram image 
            file.

    Returns:

        int: The return code of the SoX process.
    """

    sox_cmd = build_spectro_command(*spectro_params)

    result = os.system(sox_cmd)

    return result


def get_spectro_info(file_path, **segment_params):
    """Get information on spectrograms to be generated from one audio file.  

    Args:

        file_path (Pathlike): Path to an audio file.

        segment_params: Additional keyword arguments that will be passed to 
            segment_audio defining the audio segments from which spectrograms
            will be generated. Options include `seg_dur` (duration of each 
            audio segment in seconds), `interval` (time in seconds from the 
            start of each segment to the start of the next segment), and 
            `min_seg_dur` (minimum duration in seconds for segments to be 
            generated).

    Returns:

        list: List of tuples containing information on the set of spectrograms 
        that will be generated from the audio file, including offset, duration,
        and the name of the resulting image file.
    """

    try:
        offsets, durations = zip(*segment_audio(file_path, **segment_params))

        part_labels = [f"part_{i}" for i in number_items(offsets, pad=3)]

        gram_names = [Path(add_suffix(file_path, i)).with_suffix('.png').name for i in part_labels]

        path_list = [str(file_path) for i in gram_names]

        return list(zip(path_list, offsets, durations, gram_names))
    except:
        return []


def prep_spectro_gen(audio_files, dst_dir, n_chunks=None, **segment_params):
    """Generate commands to create spectrograms from a set of audio files.

    Args:

        audio_files (list): List of paths (pathlib.Path or str) to audio files
            from which spectrograms will be generated.

        dst_dir (Pathlike): Path to a folder where spectrograms will
            be generated. Will be created if it does not already exist.

        n_chunks (int): Number of subfolders to create within the destination
            folder (helps to not bog down the filesystem).

        segment_params: Optional keyword arguments that will be passed to 
            pwntools.utils.audio.segment_audio. Valid options include 
            `seg_dur`, `interval`, and `min_seg_dur`. 

    Returns:

        tuple: A tuple containing: [1] the list of unique output directories, 
        and [2]: the list of values that will be used to generate commands to 
        be executed by SoX.
    """

    gram_info_list = [get_spectro_info(i, **segment_params) for i in audio_files]

    gram_info = [x for x in flatten_list(gram_info_list) if x is not None]

    src_files, offsets, durations, dst_files = zip(*gram_info)

    n_grams = len(dst_files)

    if not n_chunks:
        chunks = [gram_info]
        dst_paths = [Path(dst_dir, "images", i) for i in dst_files]
    else:
        grams_per_chunk = n_grams // n_chunks + (0 if n_grams % n_chunks == 0 else 1) 
        dst_chunks = split_list(dst_files, grams_per_chunk)
        dst_paths = []
        for i in range(n_chunks):
            dst_paths = dst_paths + [str(Path(dst_dir, f"Part_{i+1:02d}", "images", j)) for j in dst_chunks[i]]

    out_dirs = sorted(list(set([i.parent for i in dst_paths])))

    gram_vals_for_sox = list(zip(src_files, offsets, durations, dst_paths))

    return (out_dirs, gram_vals_for_sox)

