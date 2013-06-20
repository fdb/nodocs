from glob import glob
from xml.etree import ElementTree

import os.path
from flask import Flask, render_template


GITHUB_BRANCH_NAME = 'master'
NODOCS_ROOT = os.path.dirname(os.path.abspath(__file__))
SOURCE_ROOT = os.path.dirname(NODOCS_ROOT)
NODE_LIBRARIES_DIRECTORY = os.path.join(SOURCE_ROOT, 'nodebox', 'libraries')

app = Flask(__name__)


def _find_by_name(objects, name):
    """Find an object in the list of objects that has a name attribute that matches the given name."""
    matching_objects = [o for o in objects if o.name == name]
    if len(matching_objects) == 1:
        return matching_objects[0]
    else:
        return None


class JavaScriptLibrary(object):

    @classmethod
    def from_file(cls, fname):
        source = open(fname).read()
        return JavaScriptLibrary(fname, source)

    def __init__(self, fname, source):
        self.fname = fname
        self.source = source

    def contains_function(self, functionId):
        ns, fn = functionId.split('/')
        jsId = '%s.%s' % (ns, fn)
        if jsId in self.source:
            return True
        else:
            return False


class Library(object):
    @classmethod
    def from_directory(cls, dirname):
        library_name = os.path.basename(dirname)
        library_fname = os.path.join(dirname, '%s.ndbx' % library_name)
        library = Library(library_name)
        et = ElementTree.parse(open(library_fname))
        for e in et.findall('link'):
            language, fname = e.attrib['href'].split(':')
            if language == 'javascript':
                library.modules.append(JavaScriptLibrary.from_file(os.path.join(dirname, fname)))
        root_node = et.find('node')
        library.description = root_node.attrib.get('description', 'No description')
        # Can't use a list comprehension here since we need prototype nodes to be available in self.nodes.
        for e in root_node.findall('node'):
            library.nodes.append(Node.from_element(library, e))
        return library

    @classmethod
    def find(cls, name):
        return _find_by_name(all_libraries, name)

    def __init__(self, name):
        self.name = name
        self.nodes = []
        self.modules = []

    @property
    def absolute_url(self):
        return '/%s' % self.name

    @property
    def directory(self):
        return os.path.join(NODE_LIBRARIES_DIRECTORY, self.name)

    @property
    def file(self):
        return os.path.join(self.directory, '%s.ndbx' % self.name)

    def contains_function(self, functionId):
        for m in self.modules:
            if m.contains_function(functionId):
                return True
        return False

    @property
    def all_nodes_count(self):
        return len(self.nodes)

    @property
    def javascript_nodes_count(self):
        return len([n for n in self.nodes if n.javascript_implementation])

    @property
    def javascript_progress(self):
        return round((self.javascript_nodes_count/ float(self.all_nodes_count)) * 100)

    def find_node(self, name):
        return _find_by_name(self.nodes, name)


class Node(object):
    @classmethod
    def from_element(cls, library, e):
        n = Node(library, e.attrib['name'])
        n.prototype = library.find_node(e.attrib.get('prototype'))
        n.description = e.attrib.get('description')
        n.function = e.attrib.get('function')
        n.javascript_implementation = library.contains_function(n.function)
        n.slow = n.function is not None and n.function.startswith('py')
        n.image = e.attrib.get('image')
        n.output_type = e.attrib.get('outputType', n.prototype and n.prototype.output_type)
        n.ports = [Port.from_element(n.name, pe) for pe in e.findall('port')]
        return n

    def __init__(self, library, name):
        self.library = library
        self.name = name

    @property
    def image_url(self):
        if self.image is not None:
            return 'http://github.com/nodebox/nodebox/raw/%s/libraries/%s/%s' % \
                   (GITHUB_BRANCH_NAME, self.library.name, self.image)
        else:
            return 'http://placehold.it/26x26'


class Port(object):
    @classmethod
    def from_element(cls, node, e):
        p = Port(node, e.attrib['name'])
        p.type = e.attrib.get('type')
        p.value = e.attrib.get('value')
        return p

    def __init__(self, node, name):
        self.node = node
        self.name = name


@app.route('/')
def index():
    return render_template('library_list.html', libraries=all_libraries)


@app.route('/favicon.ico')
def favicon():
    return ''


@app.route('/<library_name>')
def library_detail(library_name):
    library = Library.find(library_name)
    return render_template('library_detail.html', library=library)


@app.route('/<library_name>/<node_name>')
def node_detail(library_name, node_name):
    library = Library.find(library_name)
    node = library.find_node(node_name)
    return render_template('node_detail.html', library=library, node=node)


# Global setup
library_directories = glob(os.path.join(NODE_LIBRARIES_DIRECTORY, '*'))
all_libraries = [Library.from_directory(dirname) for dirname in library_directories]

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
