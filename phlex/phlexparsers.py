import yaml
import markdown
from .phlexstructure import PageData
from jinja2 import Template
import os


class PhlexPageParser(object):

    def __init__(self, page_data, page_tree):
        self._page = page_data
        self._page_tree = page_tree

        self._body_lines = []
        self._context = {}
        self._templates = []

        self.parse_data()

    def parse_data(self):
        pass

    def build_page(self):
        pass


class YAMLDownParser(PhlexPageParser):
    def parse_data(self):
        lines = self._page.data.splitlines()

        flag = None
        body_lines = []
        meta_lines = []
        template_lines = []
        for line in lines:
            line = line.strip()
            if line == '==>context':
                flag = 'context'
                continue
            elif line == '<==context':
                flag = None
                all_meta = yaml.load(os.linesep.join(meta_lines))
                meta_lines = []
                self._context.update(all_meta)
                continue
            elif line == '==>jinja':
                flag = 'template'
                continue
            elif line == '<==jinja':
                flag = None
                template = os.linesep.join(template_lines)
                template_lines = []
                temp = Template(template)
                self._templates.append(temp)
                body_lines.append("<==jinja:{}==>".format(len(self._templates)-1))
                continue

            if flag == 'context':
                meta_lines.append(line)
            elif flag == 'template':
                template_lines.append(line)
            else:
                body_lines.append(line)

        # auto-generate link
        if 'href' not in self._page.context:
            self._page.context['href'] = '/'.join([self._page.path_only, self._page.filename + '.html'])

        self._body_lines = body_lines
        self._page.context.update(self._context)

    def build_page(self):
        # nested data
        for key, value in self._context.items():
            if type(value) is str and value.startswith("datafrom=>"):
                fromkey = value.split('=>')[1].strip()
                datacollection = self._page_tree.find(fromkey, list)
                if not datacollection:
                    self._context[key] = []
                    continue
                datacollection = list(map(lambda x: x.context, filter(lambda i: type(i) is PageData, datacollection)))
                self._context[key] = datacollection
                self._page.context[key] = datacollection

        final_body_lines = []
        for line in self._body_lines:
            if line.startswith('<==jinja:'):
                index = int(line.split(':')[1].split('=')[0])
                template = self._templates[index]
                output = template.render(**self._context)
                final_body_lines.append(output)
            else:
                final_body_lines.append(line)

        self._page.body = markdown.markdown(os.linesep.join(final_body_lines))
