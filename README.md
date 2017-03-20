# phlex
Simple, flexible static HTML builder written in Python.

# Features
- Cross platform.
- Extensible: custom parsers can be used to handle custom file formats.
- Python 3
- Can work with other workflows. For example, using it to process the HTML
as part of a [Gulp](https://gulpjs.com/) task.

# Requirements

- Python 3.x (Python 2.7 support coming soon)
- pyyaml (for default document parser)
- markdown (for default document parser)
- jinja2 (for default document parser)

# Installation

## via pip

Coming soon.

## pip + github

### Latest Release
Use:

    $ pip install git+https://github.com/lxndrdagreat/phlex.git
  
Required modules will be install automatically.
 
### Development
Use:

    $ pip install git+https://github.com/lxndrdagreat/phlex.git@develop

Required modules will be install automatically.

# Usage

Running it is as simple as running the CLI tool from your project's directory:

    $ ./phlex
    
# Configuration

## Source
`--source` can be used to set the directory (or file) for phlex to load.
 Shortcut is `-s`. Defaults to `./src/pages`.

Example:

    $ ./phlex --source path/to/pages
    
## Templates
You can set the path to the templates directory with `--templates` or `-t`.
Default is `./src/templates`.

Example:

    $ ./phlex --templates path/to/templates
    
## Output Directory
By default, phlex outputs to the `./dist` folder. Use `--output` or `-o`
to change the output path.

Example:

    $ ./phlex --output path/to/output/directory
    
## Config File
Instead of supplying all of the different settings via the commandline, you can instead
point the program to a JSON configuration file with `--config`. `-c` can also be used 
as a shortcut.

Example:
    
    $ ./phlex --config path/to/file.json
    
Example config file:
```json
{
  "source": "path/to/source/files",
  "output": "path/to/output/directory"
}
```