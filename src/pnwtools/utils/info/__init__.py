"""
`pnwtools.utils.info`

Defines functions for producing informative console messages, log files, etc.

Functions:

    make_banner_message
        Add borders and padding to a message for emphasis.

    log_message
        Print a message while simultaneously writing it to a log file.

    print_list
        Print a list to the console with one element on each line.

    print_prog_bar
        Print a nicely formatted progress bar.

    recite_list
        Recite list elements verbally.

Classes:

    Prog_Logger
        Prints messages while optionally also writing them to a log file.
"""


def make_banner_message(message, pad_char='#', width=80):
    """Add borders and padding to a message for emphasis.

    Args:

        message (str): Message to be printed *emphatically.*

        pad_char (char): Character to be used to pad the message.

        width (int): Width of the printed message.

        print (bool): Whether to print the formatted message in 
            addition to returning it.

    Returns:

        str: The formatted message.
    """

    msg = '  ' + message + '  '
    msg_len = len(msg)
    if msg_len % 2 > 0:
        msg = msg + ' '
        msg_len = msg_len + 1

    pad_len = (width - msg_len) // 2
    pad = pad_char * pad_len

    p1 = "\n" + pad_char * width
    if msg_len > width:
        p2 = msg
    else:
        p2 = pad + msg + pad
    p3 = pad_char * width + "\n"

    formatted_message = '\n'.join([p1, p2, p3])

    return formatted_message


def log_message(message, log_path=None):
    """Print a message while simultaneously writing it to a log file.

    Args:

        log_path (str or pathlib.Path): Path to a log file where the message
            will be recorded in addition to being printed.

        message (str): Message to be logged.

    Returns:

        Nothing.
    """

    if log_path:
        with open(log_path, 'a') as log_file:
            log_file.write(message + '\n')

    print(message)

    return


def print_list(list_to_print):
    """Print a list to the console with one element on each line.

    Args:

        list_to_print (sequence): Nominally a list of elements to be printed,
            but technically any sequence or iterable should work (use caution
            with iterables whose length is not known in advance).

    Returns:

        Nothing.
    """

    print('\n'.join([str(i) for i in list_to_print]))

    return


def print_prog_bar(done, total, width=40, empty_char=".", full_char="#"):
    """Print a nicely formatted progress bar during processing.

    Assumes that you are applying some action to each element in a list or 
    sequence whose size is known in advance, and represents progress as the
    proportion of elements that have been processed.

    Args:

        done (int): Number of elements that have been completed.

        total (int): Number of elements in the entire sequence.

        width (int): Desired width of the progress bar in characters.

        empty_char (str): Character used to represent the unfinished portion of 
            the sequence. Should be a single character.

        full_char (str): Character used to represent the completed portion of 
            the sequence. Should be a single character.

    Returns:

        Nothing.
    """

    prop_done = (done / total)
    n_digits = len(str(total))

    n_full = max(0, int(width * prop_done))
    n_empty = width - n_full

    if n_full >= width:

        prog_bar = f"[{full_char*width}]"
        end_char = "\n"
    else:
        prog_bar = f"[{full_char*n_full}{empty_char*n_empty}]"
        end_char = "\r"

    prog_info = f"{str(done).rjust(n_digits, ' ')}/{total} ({prop_done*100:.1f}%)"

    prog_message = f"{prog_bar} {prog_info}"

    print(prog_message, end=end_char)

    return


def recite_list(list_to_join, oxford_comma=True):
    """Recite list elements verbally.

    Args:

        list_to_join (sequence): A list or sequence of items that can be 
            represented as strings.

        oxford_comma (bool): Include an Oxford comma after the penultimate 
            element if ``len(list_to_join)`` >= 3.

    Returns:

        str: A verbal summary of the elements of the sequence, e.g. 'Alice' for
        one element, 'Alice and Bob' for two elements, or 'Alice, Bob, and 
        Carol' for three or more elements (will get unwieldy with long lists).
    """

    str_elems = [str(x) for x in list_to_join]

    if len(list_to_join) == 1:
        pretty = str_elems[0]
    elif len(list_to_join) == 2:
        pretty = ' and '.join(list_to_join) 
    else:
        p1 = ', '.join(str_elems[:-1])
        oc = ',' if oxford_comma else ''
        pretty = f"{p1}{oc} and {str_elems[-1]}"

    return pretty


class Prog_Logger:
    """Prints messages while optionally also writing them to a log file."""

    def __init__(self, log_path=None):
        """Initialize the object with a path to a log file.
        
        Args:
        
            log_path (str or pathlib.Path): Path to a log file where 
                messages will be saved. If not provided, messages passed 
                to the object will simply be printed.
        """

        self.log_path = log_path

    def log(self, message):
        """Print a message and write it to the log file if one was provided.

        Args:

            message (str): A message to be printed and written to the 
                log file, if there is one.
        """

        log_message(message, self.log_path)

