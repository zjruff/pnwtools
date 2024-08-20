# pnwtools

`pnwtools` is a collection of software tools intended to be useful for
researchers and technicians with the USDA Forest Service Pacific 
Northwest Research Station, specifically those involved in passive 
acoustic monitoring of Northern spotted owls and other forest wildlife.
These tools may also be useful to others doing bioacoustics work but
please note that they are mostly designed for use within the USFS 
spotted owl monitoring program and will reflect its various 
idiosyncrasies.

`pnwtools` is structured as a Python package for ease of distribution 
via [the Python Package Index (PyPI.org)](https://pypi.org/project/pycnet-audio/)
but mostly consists of a collection of scripts that can be run as 
standalone command-line tools. See the Scripts section below for notes 
on the available scripts and how to use them.

This package is intended to be a living collection and will be updated 
periodically with new scripts and improvements to existing scripts. If 
there are tools or features you would like to see added, please email 
Zack via zjruff at gmail dot com.

# Installation

`pnwtools` is compatible with all modern versions of Python (2.7 and 
3+) and can be installed using `pip` like so:

```
python -m pip install pnwtools
```

Note that there is an unrelated package called `pwntools` which 
provides tools for Capture The Flag-style cybersecurity competitions. 
The similar spelling makes it very easy to install this other package 
by mistake, so we recommend simply copying and pasting the above 
command into your shell program.

To make sure you are using the latest available version of `pnwtools`,
you can update it at any time like so:

```
python -m pip install --upgrade pnwtools
```

This will search PyPI for a version of `pnwtools` that's newer than the
one you have installed; if there is a newer version available, pip will 
install it for you.

# Scripts

