
Welcome to pnwtools
======================

``pnwtools`` is a Python package that provides useful tools for processing
audio data for bioacoustics research. It provides a Python API and a number of
standalone scripts to automate various aspects of the bioacoustics workflow.

.. toctree::
   :maxdepth: 2
   :caption: Contents

   pnwtools <pnwtools>

Installation
======================

pnwtools can be installed from the `Python Package Index <https://pypi.org/>`_
using ``pip``. It is compatible with Python versions 3.8 and later. For best
performance when working with WAV files, we recommend Python versions < 3.12;
the ``chunk`` module was officially removed from the standard library in 3.12 
and this makes it significantly less efficient to dig through WAV files to find
metadata. Assuming you have a compatible Python environment set up, just run
::

	python -m pip install pnwtools


This will also install several dependencies, including `pandas 
<https://pandas.pydata.org/pandas-docs/version/2.3/index.html>`_, `soundfile 
<https://pypi.org/project/soundfile/>`_, `fastparquet 
<https://pypi.org/project/fastparquet/>`_, and `guano 
<https://guano-py.readthedocs.io/en/latest/api.html>`_.

In addition to providing the importable ``pnwtools`` Python module, installation
with pip will also add a number of scripts to the path so that they can be 
invoked from the command line, providing a flexible interface for various tasks.
These scripts and the available options are described below.

Scripts
======================




