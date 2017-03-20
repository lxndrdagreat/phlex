# phlex
Simple, flexible static HTML builder written in Python.

# Features
- Cross platform.
- Extensible: custom parsers can be used to handle custom file formats.
- Python 3
- Can work with other workflows. For example, using it to process the HTML
as part of a [Gulp](https://gulpjs.com/) task.

# Installation

## via pip

## from github

### Latest Release
Install with `pip install git+https://github.com/lxndrdagreat/phlex.git`
 
### Development
Install with `pip install git+https://github.com/lxndrdagreat/phlex.git@develop`


# Usage

Running it is as simple as running the CLI tool from your project's directory:

    $ phlex
    
# Configuration

## Config File
Instead of supplying all of the different settings via the commandline, you can instead
point the program to a JSON configuration file with `--config path/to/file.json`. `-c` can
also be used as a shortcut.

