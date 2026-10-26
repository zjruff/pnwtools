# pnwtools

`pnwtools` is a collection of software tools intended to be useful for
researchers and technicians with the USDA Forest Service Pacific 
Northwest Research Station, specifically those involved in passive 
acoustic monitoring of Northern spotted owls and other forest wildlife.

`pnwtools` is structured as a Python package for ease of distribution 
via the [Python Package Index](https://pypi.org/project/pnwtools/).
The package contains a Python module called `pnwtools` with a number of 
submodules. A number of standalone scripts are also provide for 
everyday tasks. See [Scripts](#scripts) below for notes on these tools 
and how to use them. We are working on a new documentation page to 
provide more comprehensive instructions; it will be available at 
https://pnwtools.readthedocs.io when finished.

This package is very much a living resource and will be updated 
periodically with new scripts as well as bug fixes, improvements, etc.
If there are tools or features you would like to see added, or if 
something is not working correctly, please email me (Zack) and we can
talk about it. (You can open an issue on GitHub if you really want to, 
but I respond better to email.)

## Installation

`pnwtools` is compatible with Python versions 3.8+ and can be installed
from the Python Package Index (PyPI) using `pip` like so:

```
python -m pip install pnwtools
```

To update to the latest version, run

```
python -m pip install --upgrade pnwtools
```

To uninstall, run

```
python -m pip uninstall pnwtools
```

## Scripts

These are meant to provide a lot of utility for day-to-day work and are
structured as simple command-line tools. When you install `pnwtools` 
via `pip`, the scripts can be invoked by name from the command line, 
along with any arguments. Note that if you installed `pnwtools` in a 
conda environment, the scripts will only work when that environment is 
active.

## Functional API

As of this version, we have expanded and reorganized `pnwtools` in an
attempt to provide a more complete and useful API for processing audio 
data in Python. Some of the new functionality has been ported over from
`pycnet-audio`, which now formally depends on `pnwtools`. This is to 
increase the package's overall usefulness, reduce duplication, and make
it easier to maintain both packages.

Generally, there is an umbrella module, `pnwtools`, with a submodule 
called `utils`, which in turn contains a number of sub-submodules that 
define useful functions and classes for various aspects of biaocoustic
data processing.

