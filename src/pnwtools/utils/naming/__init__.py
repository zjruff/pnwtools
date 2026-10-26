"""
`pnwtools.utils.naming`

Defines functions for creating, parsing, and modifying structured filenames.

Functions:

    add_suffix
        Add a suffix to a filename, before the file extension.

    build_filename
        Construct a filename from an arbitrary sequence of parts.

    build_prefix
        Construct a prefix from path wildcards and/or arbitrary strings.

    build_prefix_2
        Construct a prefix from path components.

    get_prefix
        Extract the part of a filename preceding the timestamp.

    mass_rename
        Rename many files based on a renaming table.

    prep_mass_rename
        Build a table linking old and new filenames in advance of renaming.

    read_rename_log
        Read a log file previously generated from a renaming operation.

    remove_pattern
        Remove a suffix matching a pattern from a filename.

    rename_file
        Rename a single file.

    replace_prefix
        Selectively replace part of a filename with a new text.
"""

import re
from datetime import datetime, timedelta
from pathlib import Path
from pnwtools.utils.lists import number_items
from .timestamp import *

def add_suffix(filename_orig, suffix):
    """Add a suffix to a filename, before the file extension.

    Args:

        filename_orig (str): The current filename.

        suffix (str): Suffix to add to the filename.

    Returns:

        str: Modified filename created by adding the specified suffix to the 
        original filename.
    """

    path_orig = Path(filename_orig)

    ext, stem = path_orig.suffix, path_orig.stem

    new_filename = f"{stem}_{suffix}{ext}"

    return new_filename


def build_filename(*parts, sep='_'):
    """Construct a filename from an arbitrary sequence of parts.

    This function does not include the file extension. Use 
    pathlib.Path.with_stem to replace the actual filename while leaving the 
    original file extension unchanged.

    Args:

        parts (sequence): A sequence of elements that will be joined to create 
            the filename. These elements will be coerced to strings before they
            are joined together.

        sep (str): Character or string that will be used to join the parts.

    Returns:

        str: New filename created by joining the provided parts.
    """

    new_name = sep.join([str(p) for p in parts])

    return new_name


def build_prefix(path_orig, prefix_string=None):
    """Build a filename prefix from a file's location and/or arbitrary strings.

    Valid wildcards include: 
    ``%p``, the name of the file's parent folder; 
    ``%g``, the name of the file's "grandparent" folder (the parent folder of 
    the parent folder); 
    ``%c``, the partial parent folder, i.e. the last component of the parent 
    folder's name split up by underscores; and 
    ``%h``, the partial grandparent folder, i.e. the last component of the 
    grandparent folder's name split up by underscores.

    Args:

        file_path (pathlib.Path or str): Full path to the file for which a 
            prefix will be generated.

        prefix_string (str): Prefix to use, which may include one or more
            wildcards that will be replaced with components of the path.

    Returns:

        str: The prefix created by substituting the appropriate path
        components for their corresponding wildcards in the prefix
        string provided.
    """

    file_path = Path(path_orig)
    comps = file_path.parent.parts

    parent_dir, grandparent_dir = comps[-1], comps[-2]

    partial_parent = parent_dir.split('_')[-1]
    partial_grandparent = grandparent_dir.split('_')[-1]

    replacements = {"%p": parent_dir, 
                    "%g": grandparent_dir, 
                    "%c": partial_parent,
                    "%h": partial_grandparent}

    for patt in replacements:
        prefix_string = re.sub(patt, replacements[patt], prefix_string)

    return prefix_string


def build_prefix_2(fpath, depth=2, sep='-', ignore=None):
    """Construct a prefix from path components.

    Args:

        file_path (pathlib.Path or str): Full path to a file for which a prefix 
            should be constructed.

        depth (int): Number of levels of enclosing directories to include
            in the prefix; 1=parent, 2=grandparent and parent, etc.

        sep (str): Character(s) to use to divide path components in the new
            file prefix.

        ignore (str): String that should be omitted from the prefix if it 
            occurs in the path.

    Returns:

        str: New prefix for the filename.
    """

    parts = Path(fpath).parent.parts

    if ignore:
        dirs = [x.replace(ignore, '') for x in parts]
    else:
        dirs = parts

    prefix = sep.join(dirs[-depth:])

    return prefix


def get_prefix(filename):
    """Extract the part of a filename preceding the timestamp.

    Args:

        filename (str): String representing a filename.

    Returns:

        str: String representing a prefix obtained by removing the file 
        extension and any timestamp information.
    """

    file_stem = Path(filename).stem

    stamp_patt = re.compile("_20[0-9]{6}_[0-9]{6}$")

    stamp_match = re.search(stamp_patt, file_stem)

    if not stamp_match:
        prefix = file_stem
    else:
        prefix = re.sub(stamp_patt, '', file_stem)

    return prefix


def mass_rename(rename_vals, reverse=False):
    """Apply a renaming operation to many files.

    Args:

        rename_vals (sequence): A sequence of sequences representing the folder
            location, original filename, and new filename for each of a set of
            files.

        reverse (bool): Apply renaming in reverse order, i.e., revert each file
            to its original name.

    Returns:

        list: A list of integers indicating whether each individual renaming 
        operation was successful (1), produced no change (0), or produced an
        error (-1).
    """

    folders, old_names, new_names, changed = zip(*rename_vals)

    old_paths = [Path(*x) for x in zip(folders, old_names)]
    new_paths = [Path(*y) for y in zip(folders, new_names)]

    if reverse:
        result = [rename_file(*z) for z in zip(new_paths, old_paths)]
    else:
        result = [rename_file(*z) for z in zip(old_paths, new_paths)]

    return result


def prep_mass_rename(file_list, new_prefix, number_files=False):
    """Build a table linking old and new filenames in advance of renaming.

    Args:

        file_list (list): List of paths to the files that will be renamed.

        prefix (str): A prefix to use to construct new filenames. May contain 
            wildcards corresponding to path components as well as arbitrary 
            strings.

        number_files (bool): Number files sequentially rather than using 
            timestamps.

    Returns:

        list: A list of tuples containing the folder location, original 
        filename, and updated filename for each file.
    """

    folders, old_names, exts = zip(*[(str(i.parent), i.name, i.suffix) for i in file_list])

    new_prefixes = [build_prefix(i, new_prefix) for i in file_list]

    if number_files:
        file_ids = number_items(file_list)
    else:
        file_ids = [get_timestamp(f) for f in old_names]

    new_stems = [build_filename(*j) for j in zip(new_prefixes, file_ids)]

    new_names = [''.join(k) for k in zip(new_stems, exts)]
    
    changes = [1 if i[0] != i[1] else 0 for i in zip(old_names, new_names)]

    rename_info = list(zip(folders, old_names, new_names, changes))

    return rename_info


def read_rename_log(log_file_path):
    """Read a log file generated from a previous renaming operation.

    Args:

        log_file_path (pathlib.Path or str): Path to the log file. Log file 
            should be comma-delimited and have three columns representing the
            folder location, original filename, and current filename for each
            of a set of files, as well as a Result column indicating whether 
            each filename was changed (1), stayed the same (0), or could not be
            changed due to an error (-1).

    Returns:

        list: List of lists representing the folder location, original 
        filename, current filename, and the effect of the previous renaming 
        operation on each of a set of files. 
    """

    if not Path(log_file_path).exists():
        raise FileNotFoundError
    else:
        with open(log_file_path) as log_file:
            log_vals = [line.rstrip().split(',') for line in list(log_file)[1:]]

    return log_vals


def remove_pattern(filename, remove_patt):
    """Remove a suffix matching a pattern from a filename.

    Args:

        filename (str): Filename to be modified.

        remove_patt (re.pattern): Regular expression encoding the format of the
            suffix to be removed. 

    Returns:

        str: Filename created by removing suffix matching the prefix pattern,
        or the original filename if the pattern did not produce a match. 
    """

    mod_filename = re.sub(remove_patt, '', filename)

    return mod_filename


def rename_file(src_path, dst_path):
    """Rename a single file.

    Args:

        src_path (pathlib.Path or str): The current path of the file.

        dst_path (pathlib.Path or str): The desired path of the file after 
            renaming.

    Returns:

        int: 1 if the renaming was successful, 0 if the paths are the same 
        (i.e., no renaming occurred), or -1 if the renaming operation produced
        an error.
    """

    if src_path == dst_path:
        return 0
    else:
        try:
            Path(src_path).rename(dst_path)
            return 1
        except:
            return -1


def replace_prefix(filename_orig, new_prefix, old_prefix=None):
    """Selectively replace part of a filename with a new text.

    Args:

        filename_orig (str): Filename to be modified.

        new_prefix (str): Prefix to be used in the updated filename. This will
            immediately precede the filename timestamp.

        old_prefix (str): Prefix to replace with the new prefix. If this is 
            unspecified, the part to be replaced will be determined using 
            infer_prefix.

    Returns:

        str: Updated filename with the new prefix.
    """

    if not old_prefix:
        to_replace = get_prefix(filename_orig)
    else:
        to_replace = old_prefix

    new_filename = filename_orig.replace(to_replace, new_prefix)

    return new_filename


