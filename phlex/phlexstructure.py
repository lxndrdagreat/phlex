import os


def split_path(path):
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path: # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts


class PageData(object):
    def __init__(self, path, data):
        self.source_path = path
        self.path = split_path(path)
        self.path_only = os.path.join(*self.path[0:-1]) if len(self.path) > 1 else ''
        self.collection = self.path[-2] if len(self.path) > 1 else ''
        self.filename = os.path.splitext(self.path[-1])[0]
        self.data = data
        self.file_type = os.path.splitext(path)[1]
        self.context = {}
        self.body = None
        self.parser = None

    def assign_parser(self, parser, page_tree):
        self.parser = parser(self, page_tree)


class TreeStructure(object):
    def __init__(self, startingpath):
        self.base_dir = startingpath
        self._pages = []
        self._starting_path = startingpath
        self._structure = None

    def crawl(self):
        self._structure = self._get_structure(self._starting_path)

    def find(self, search, kind=None):
        return self._find(search, self._structure, kind)

    def _find(self, search, node, kind=None):
        if not node:
            return None

        if type(node) is dict:
            if search in node and (kind is None or type(node[search]) is kind):
                return node[search]
            for key, value in node.items():
                found = self._find(search, value, kind)
                if found:
                    return found
            return None
        elif type(node) is list:
            for item in node:
                found = self._find(search, item, kind)
                if found:
                    return found
            return None
        elif type(node) is PageData and (kind is None or kind is PageData):
            if node.filename == search:
                return node
            else:
                return None
        else:
            return None

    @staticmethod
    def get_page_contents(page_path):
        contents = ""
        with open(page_path, 'r') as page_file:
            contents = page_file.read()

        return contents

    def _get_structure(self, startpath):
        file_folder_dict = {os.path.basename(startpath): []}
        if not os.path.exists(startpath):
            return None
        if not os.path.isfile(startpath):
            try:
                for f in os.listdir(startpath):
                    subfolder = os.path.join(startpath, f)
                    file_folder_dict[os.path.basename(startpath)].append(self._get_structure(subfolder))
            except Exception as e:
                print(e)
        else:
            if os.path.splitext(startpath)[1] == '.yd':
                base_parts = split_path(self.base_dir)
                final_parts = split_path(startpath)[len(base_parts):]
                final_path = os.path.join(*final_parts) if len(final_parts) > 1 else final_parts[0]
                page_data = TreeStructure.get_page_contents(startpath)
                page = PageData(final_path, page_data)
                self._pages.append(page)
                return page
            else:
                return None
        return file_folder_dict

    def pages(self):
        return self._pages

    def print_tree(self, node=None, path=[]):
        if not node and len(path) == 0:
            node = self._structure

        indent = ""
        indenter = "  "
        for i in range(0, len(path)):
            indent += indenter

        if not node:
            return
        if type(node) is dict:
            for key, value in node.items():
                print(indent + key + '/')
                new_path = list(path)
                new_path.append(key)
                self.print_tree(value, new_path)
        elif type(node) is list:
            for item in node:
                self.print_tree(item, list(path))
        elif type(node) is PageData:
            print(indent + node.filename)