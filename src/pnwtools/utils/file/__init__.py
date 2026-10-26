"""
`pnwtools.utils.file`

Defines functions for basic file handling and filesystem manipulation.

Functions:

    find_files
        Find files with specific file extension(s) within a directory tree.

    find_folders
        Find folders within a directory tree.

    get_file_info
        Get basic information about a single file.

    get_unique_extensions
        List unique file extensions that occur within a directory tree.

    make_file_dict
        Build a dictionary of file paths indexed by filenames.

    parse_extensions
        Create a list of properly formatted file extensions (i.e., suffixes) 
        from a string.
"""

import os
import re
from pathlib import Path
from pnwtools.utils.lists import listify


def find_files(top_dir, ext):
    """Find files with certain file extension(s) in a directory.

    Extensions will have an initial period added if they do not already have 
    one. Extension matching is case-insensitive.

    Args:

        top_dir (pathlib.Path or str): Path to the root of the directory tree 
            to be searched.

        ext (str or sequence): List of file extensions to be matched.

    Returns:

        list: Sorted list of pathlib.Path objects representing files with the 
        specified extension(s) in the directory tree.
    """

    ext_list = parse_extensions(ext)

    matched = [f for f in Path(top_dir).rglob('*') if f.suffix.lower() in ext_list]

    return sorted(matched)


def find_folders(top_dir):
    """Find folders within a directory tree.
    
    Args:
    
        top_dir (pathlib.Path or str): Path to the root of the directory tree 
            to be searched.

    Returns:
    
        list: List of pathlib.Path objects representing folders within the 
        directory tree.
    """

    dirs = [d for d in Path(top_dir).rglob("*") if d.is_dir()]

    return sorted(dirs)


def get_file_info(file_path):
    """Get basic information about a single file.

    Args:

        file_path (pathlib.Path or str): Path to the file.

    Returns:

        dict: Dictionary listing the file's parent directory, name, size in 
        bytes, and last modification time.
    """

    fpath = Path(file_path)

    file_info = {"dir": fpath.parent,
                 "name": fpath.name,
                 "size": os.path.getsize(file_path),
                 "mtime": os.path.getmtime(file_path)}

    return file_info


def get_unique_extensions(top_dir):
    """List unique file extensions that occur within a directory tree.
    
    Args:
    
        top_dir (pathlib.Path or str): Path to the root of the directory tree.

    Returns:
    
        list: List of all unique file extensions that occur within the 
        directory tree.
    """

    ext_list = [f.suffix for f in Path(top_dir).rglob("*") if not f.is_dir()]

    unique_extensions = sorted([e for e in set(ext_list)])

    return unique_extensions


def make_file_dict(file_list):
    """Create a dictionary of file paths indexed by filenames.

    Args:

        file_list (list): List of file paths, as returned by find_files.

    Returns:

        dict: Dictionary of file paths indexed by filename.
    """

    file_dict = dict(zip([f.name for f in file_list], file_list))
    
    return file_dict


def parse_extensions(ext_str):
    """Create a list of properly formatted file extensions from a string.

    Args:

        ext_str (str): A string listing one or more file extensions separated
            by commas.

    Returns:

        list: A list of strings representing file extensions. A dot will be 
        prepended to each extension if it did not already have one.
    """

    ext = listify(ext_str)

    ext_list = []

    for i in ext:
        i_corr = f".{i}" if i[0] != '.' else i
        ext_list.append(i_corr.lower())

    return ext_list

