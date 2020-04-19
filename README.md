# PyScan

A command-line TUI utility for scanning images, written in Python.

## Dependencies

* `pythondialog>=3.4.0`
* `toml>=0.10.0`
* `pillow>=6.2.2`
* `python-sane` (see below)

This project uses SANE as the scanner backend, and depends on a recent revision
of the [python-sane][python-sane] package for interacting with the scanner.
However, PyScan is written in Python 3, and as of April 19, 2020, there has
been no release of the `python-sane` package containing Python 3 support.
This necessitates the package to be downloaded and installed from source;
see the instructions provided in the package repo.

## Configuration

PyScan depends on a configuration file (`${HOME}/.config/pyscan.toml`) which
describes the supported formats and scanner configurations.  A sample
configuration file is provided in `pyscan.toml.example`.

[python-sane]: https://github.com/python-pillow/Sane
