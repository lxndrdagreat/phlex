from functools import reduce

import click
import os
import json
from jinja2 import Environment, FileSystemLoader
from jinja2.exceptions import TemplateNotFound
from phlex.phlexstructure import TreeStructure
import yaml
import sys
import importlib


PHLEX_VERSION = '2.0.0'


@click.command()
@click.option('--config', '-c', default=None, help='Path to configuration file')
@click.option('--source', '-s', default=f'{os.path.join("src", "pages")}', help='Path to source page files')
@click.option('--templates', '-t', default=f'{os.path.join("src", "templates")}', help='Path to template files')
@click.option('--default-template', '-T', default=None, help='Name of default template to use')
@click.option('--output', '-o', default=f'{os.path.join("dist")}', help='Path to put completed files')
@click.option('--version', is_flag=True, help='Show current version number for Phlex and exit.')
def main(config, source, templates, default_template, output, version):
    """Flexible static HTML builder"""

    if version:
        print(f'Phlex version {PHLEX_VERSION}')
        quit()

    # scaffold the settings
    settings = {
        "PAGES": source,
        "TEMPLATES": templates,
        "DEFAULT_TEMPLATE": default_template,
        "OUTPUT": output,
        "PARSERS": {
            '.yd': 'LegacyYAMLDownParser'
        }
    }

    # import settings from config if it exists (supports JSON and YAML)
    if config and os.path.exists(config):
        with open(config, 'r') as settings_read:
            filename, file_extension = os.path.splitext(config)
            setting_file = None
            if file_extension == '.json':
                # use JSON
                setting_file = json.loads(settings_read.read())
            else:
                # YAML is default
                setting_file = yaml.load(settings_read.read())

            for key, value in setting_file.items():
                if key.upper() in settings:
                    settings[key.upper()] = value

    # check for configuration errors
    if not os.path.exists(settings['TEMPLATES']):
        raise Exception(f'Config error: could not find template path "{settings["TEMPLATES"]}"')

    if not os.path.exists(settings['PAGES']):
        raise Exception(f'Config error: could not find pages path "{settings["PAGES"]}"')

    # Assign parsers to file types
    page_parsers = settings['PARSERS']
    if not page_parsers or len(page_parsers) == 0:
        raise Exception(f'No parsers were defined.')
    for key, value in page_parsers.items():
        mod = None
        split_path = value.split('.')

        # module path provided
        if len(split_path) > 1:
            # If the module is already loaded
            if ''.join(split_path[:-1]) in sys.modules:
                try:
                    mod = reduce(getattr, ''.join(split_path[:-1]), sys.modules)
                except AttributeError as e:
                    pass
            else:
                # try to import the modules then the class
                try:
                    # get everything but the final piece
                    mods = '.'.join(split_path[:-1])
                    importlib.import_module(mods)
                    mod = reduce(getattr, split_path[-1:], sys.modules[mods])
                except ModuleNotFoundError as e:
                    pass
                except AttributeError as e:
                    pass
        else:
            # see if it exists in scope already
            try:
                mod = reduce(getattr, value.split("."), sys.modules[__name__])
            except AttributeError as e:
                pass

            # The built-in parsers that come with Phlex are the final fallback
            try:
                # import built-ins if they aren't there
                if 'phlex.phlexparsers' not in sys.modules:
                    importlib.import_module('phlex.phlexparsers')
                mod = reduce(getattr, value.split("."), sys.modules['phlex.phlexparsers'])
            except AttributeError as e:
                pass

        if mod:
            page_parsers[key] = mod
        else:
            # Could not load module and/or parser, so throw error
            raise Exception(f'Could not load parser "{value}"')

    # Create output path if it does not exist
    if not os.path.exists(settings['OUTPUT']):
        os.makedirs(settings['OUTPUT'])

    # set up jinja environment
    env = Environment(
        loader=FileSystemLoader(settings['TEMPLATES']))

    tree = TreeStructure(settings['PAGES'])
    tree.crawl()

    for page in tree.pages():
        parser = page_parsers[page.file_type](page, tree)
        page.assign_parser(page_parsers[page.file_type], tree)

    with click.progressbar(tree.pages()) as bar:
        for page in bar:
            page.parser.build_page()
            path = list(page.path)
            del path[-1]
            path.insert(0, settings['OUTPUT'])
            path.append(page.filename + '.html')

            # get template
            template = None
            try:
                template = env.get_template(page.context['template'] + '.html')
            except TemplateNotFound as e:
                raise Exception(f'Could not find template file "{page.context["template"]}" for '
                                f'page "{page.source_path}"')

            # render
            page_output = template.render(**page.context, body=page.body)

            # path safety: build the path to the page if it does not exist
            if not os.path.exists(os.path.join(*path[0:-1])):
                os.makedirs(os.path.join(*path[0:-1]))

            # save to file
            output_file_name = os.path.join(*path)
            with open(output_file_name, 'w') as write_page:
                write_page.write(page_output)
