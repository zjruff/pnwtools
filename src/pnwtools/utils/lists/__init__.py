"""
`pnwtools.utils.lists`

Defines functions for dealing with lists (and potentially other sequences).

Functions:

    flatten_list
        Turn a two-level nested list (a list of lists) into a flat list.

    has_duplicates
        Check whether an iterable contains duplicate elements.

    listify
        Convert a string to a list, or return a list unmodified.

    number_elements
        Assign a sequential number to each element of a list.

    split_list
        Split one list into one or more chunks with a maximum size.
"""


def flatten_list(nested_list):
    """Turn a two-level nested list (a list of lists) into a flat list.

    As written this only removes the first level of nesting, so multi-nested 
    lists will not be completely flattened. However, this function could be
    applied recursively to guarantee the resulting list is completely flat.
    This function effectively reverses split_list.

    Args:

        nested_list (list): A list of lists (of lists (of lists (etc.))).

    Returns:

        list: A list with the top level of nesting removed.
    """

    flat_list = []
    for i in nested_list:
        try:
            iter_i = iter(i)
            flat_list.extend(i)
        except:
            flat_list.append(i)

    return flat_list


def has_duplicates(iterable):
    """Check whether an iterable contains duplicate elements.
    
    Formally, checks whether the length of the iterable is equal to the number
    of unique elements therein.

    Args:

        iterable: An iterable such as a list, tuple, or generator.

    Returns:

        bool: True if the iterable has duplicate elements or False if all 
        elements are unique.
    """

    iter_items = [x for x in iterable]

    return len(iter_items) != len(set(iter_items)) 


def listify(seq_or_str, sep=None):
    """Convert a string to a list, or return a list unmodified.

    Just a helper function to allow find_files to accept either a single string
    or a list of strings as input.

    Args:

        seq_or_str (sequence or string): Either a single string or a sequence
            (i.e., list) of strings.

        sep (str): Will be passed to str.split in the case of string input. If 
            sep is None, string input will be wrapped in a single-element list 
            with any leading or trailing whitespace removed.

    Returns:

        seq: If the input was already a sequence it is returned unchanged. If 
        it was a single string, it is wrapped in a list with one or more 
        elements, depending on sep.
    """

    try:
        seq = seq_or_str.split(sep)
    except:
        seq = seq_or_str

    return seq


def number_items(list_orig, start=1, step=1, as_str=True, pad=None):
    """Assign a sequential number to each element of a list or sequence.

    Args:

        list_orig (list): List of items to be numbered.

        start (int): Starting point for the sequence.

        step (int): Size of the increment from one item to the next.

        as_str (bool): Return numbers as a list of formatted strings rather 
            than integers. Strings will be zero-padded.
        
        pad (int): Number of digits to use for zero-padded strings. If pad is
            None (default) the number of digits will be calculated based on the
            maximum value in the sequence.

    Returns:

        list: List of either zero-padded strings or integers representing a 
        sequential numbering of items in the original list.
    """

    n = len(list_orig)

    indices = [start + step*i for i in range(n)]

    if as_str:
        if not pad:
            n_digits = len(str(max(indices)))
        else:
            n_digits = int(pad)
        formatted = [f"{i:0{n_digits}d}" for i in indices]
        return formatted
    else:
        return indices


def split_list(list_orig, chunk_size):
    """Split one long list into one or more chunks with a maximum size.

    The returned object will always be a nested list even in cases where e.g. 
    the length of list_orig is less than or equal to chunk_size. Use 
    flatten_list to remove nesting if needed.

    Args:

        list_orig (list): A list to be split into chunks.

        chunk_size (int): Number of items to include in each chunk. If 
            len(list_orig) is not a whole-number multiple of chunk_size the 
            final chunk will be shorter.

    Returns:

        list: A list of lists representing chunks of the original list, each 
        containing at most chunk_size elements. 
    """

    n_items = len(list_orig)

    n_chunks = n_items // chunk_size + (0 if n_items % chunk_size == 0 else 1)

    chunk_indices = [i * chunk_size for i in range(n_chunks)]

    chunks = [list_orig[j : min(j+chunk_size, n_items)] for j in chunk_indices]

    return chunks


