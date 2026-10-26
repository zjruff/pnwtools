"""`pnwtools` package for working with bioacoustics data

:copyright: (c) 2026 by Zachary J. Ruff
:license: GNU General Public License v3; see LICENSE for details.
"""

import os
from importlib.metadata import version


from . import inventory 
from . import tagging 
from . import utils


__version__ = version("pnwtools")
