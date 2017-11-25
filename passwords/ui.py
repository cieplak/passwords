from collections import OrderedDict
import colorful


class Node(object):

    def __init__(self, key=None, value=None, children=None):
        children = children or Children()
        self.key = key
        self.value = value
        self.children = children

    def add_value_by_path(self, path, value, sep='.'):
        keys = path.split(sep)
        node = self
        for key in keys:
            child = node.children.add(Node(key=key))
            node = child
        node.value = value

    def str(self):
        return Printer(self).str()


class Dim(object):

    def __init__(self, depth=0, left=0, right=0):
        self.depth = depth
        self.left = left
        self.right = right


class Printer(object):

    def __init__(self, node):
        self.root = node
        self.depth = 0
        self.buffer = ''
        self.lines = []
        self.col = 0
        self.dims = [[Dim()]]

    def str(self):
        for node in self.root.children.nodes_by_key.values():
            self.descend(node)
        key_values = [s.split('=') for s in self.lines]
        tree_width = max(len(x[0]) for x in key_values)
        lines = [
            str(colorful.bold_cyan(x[0])) +
            (' ' * (tree_width - len(x[0]))) +
            str(colorful.bold_yellow(' = ')) +
            x[1]
            for x in key_values
        ]
        return '\n'.join(lines)

    def write(self, text):
        self.col += len(text)
        self.buffer += text

    def descend(self, node):
        self.depth += 1
        if len(self.dims[-1]) == 0:
            self.write_indent(node)
        self.write_key(node)
        for child in node.children.nodes_by_key.values():
            self.descend(child)
        self.ascend()

    def ascend(self):
        self.depth -= 1

    def write_indent(self, node):
        assert (len(self.dims[-1]) == 0)
        dim = Dim(left=0)
        offset = self.find_offset(node)
        indent = ' ' * offset
        self.write(indent)
        self.dims[-1].append(dim)

    def find_offset(self, node):
        depth_above = self.dims[-2][-1].depth
        if self.depth > depth_above:
            return self.dims[-2][-1].right
        if self.depth == depth_above:
            return self.dims[-2][-1].left
        for line in reversed(self.dims):
            for dim in reversed(line):
                if dim.depth == self.depth:
                    return dim.left
        return 0

    def write_key(self, node):
        dim = Dim(left=self.col, depth=self.depth)
        if self.depth > 1:
            self.write('.')
        self.write(node.key)
        dim.right = self.col
        self.dims[-1].append(dim)
        if node.value != None:
            self.write_value(node)

    def write_value(self, node):
        self.write(' = ')
        self.write(str(node.value))
        self.write_line()

    def write_line(self):
        self.lines.append(self.buffer)
        self.buffer = ''
        self.col = 0
        self.dims.append([])


class Children(object):

    def __init__(self):
        self.empty = True
        self.nodes_by_key = OrderedDict()

    def __getitem__(self, key):
        return self.nodes_by_key.get(key, Node(key=key))

    def __iter__(self):
        for node in self.nodes_by_key.values():
            yield node

    def add(self, node):
        key = node.key
        self.empty = False
        child = self.nodes_by_key.get(key)
        if child:
            if node.value != None:
                child.value = node.value
            if not node.children.empty:
                for item in node.children:
                    child.children.add(item)
        else:
            child = node
            self.nodes_by_key[key] = child
        return child
