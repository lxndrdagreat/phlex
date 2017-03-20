import click
import os
import json
from jinja2 import Environment, FileSystemLoader
from .phlexstructure import TreeStructure, PageData, split_path
from .phlexparsers import YAMLDownParser
import sys


PHLEX_VERSION = '1.0.0'


@click.command()
@click.option('--config', '-c', default=None, help='Path to configuration file')
@click.option('--source', '-s', default='{}'.format(os.path.join('src', 'pages')), help='Path to source page files')
@click.option('--templates', '-t', default='{}'.format(os.path.join('src', 'templates')), help='Path to template files')
@click.option('--default-template', '-T', default=None, help='Name of default template to use')
@click.option('--output', '-o', default='{}'.format(os.path.join('dist')), help='Path to put completed files')
@click.option('--version', is_flag=True)
def main(config, source, templates, default_template, output, version):
    """Flexible static HTML builder"""

    if version:
        print("Phlex version {}".format(PHLEX_VERSION))
        quit()

    settings = {
        "PAGES": source,
        "TEMPLATES": templates,
        "DEFAULT_TEMPLATE": default_template,
        "OUTPUT": output
    }

    if config and os.path.exists(config):
        with open(config, 'r') as settings_json_file:
            setting_file = json.loads(settings_json_file.read())
            for key, value in setting_file.items():
                settings[key] = value

    page_parsers = {
        '.yd': YAMLDownParser
    }

    tree = TreeStructure(settings['PAGES'])
    tree.crawl()

    if not os.path.exists(settings['OUTPUT']):
        os.makedirs(settings['OUTPUT'])

    env = Environment(
        loader=FileSystemLoader(settings['TEMPLATES']))

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
            template = env.get_template(page.context['template'] + '.html')
            # template.globals['context'] = get_context
            # template.globals['callable'] = callable

            # render
            page_output = template.render(**page.context, body=page.body)

            # path safety: build the path to the page if it does not exist
            if not os.path.exists(os.path.join(*path[0:-1])):
                os.makedirs(os.path.join(*path[0:-1]))

            # save to file
            output_file_name = os.path.join(*path)
            with open(output_file_name, 'w') as write_page:
                write_page.write(page_output)
