import os.path
from flask import Flask, render_template, redirect, url_for, request
from xml.etree import ElementTree

GITHUB_BRANCH_NAME = 'vertical-network-view'
NODE_LIBRARIES_DIRECTORY = '../nodebox/libraries'

app = Flask(__name__)

class Library(object):
    def __init__(self, name, description):
        self.name = name
        self.description = description

    @property
    def absolute_url(self):
        return '/%s' % self.name

    @property
    def directory(self):
        return os.path.join(NODE_LIBRARIES_DIRECTORY, self.name)

    @property
    def file(self):
        return os.path.join(self.directory, '%s.ndbx' % self.name)
        
    def find_node(self, name):
        matching_nodes = [node for node in self.nodes if node.name == name]
        if len(matching_nodes) == 1:
            return matching_nodes[0]
        else:
            return None
            
class Node(object):
    
    @classmethod
    def from_element(cls, library, e):
        n = Node(library, e.attrib['name'])
        n.description = e.attrib.get('description')
        n.function = e.attrib.get('function')
        n.image = e.attrib.get('image')
        n.output_type = e.attrib.get('outputType')
        n.prototype = e.attrib.get('prototype')
        n.ports = [Port.from_element(n.name, pe) for pe in e.findall('port')]
        return n
    
    def __init__(self, library, name):
        self.library = library
        self.name = name
        
    @property
    def image_url(self):
        if self.image is not None:
            return 'http://github.com/nodebox/nodebox/raw/%s/libraries/%s/%s' % (GITHUB_BRANCH_NAME, self.library.name, self.image)
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

all_libraries = [
    Library('color', 'Color'),
    Library('core', 'Core'),
    Library('coreimage', 'Image processing'),
    Library('corevector', 'Vector generation and filtering'),
    Library('data', 'Data manipulation'),
    Library('l_system', 'Tree generation using L-systems'),
    Library('list', 'Generic list processing'),
    Library('math', 'Generic math operations'),
    Library('packing', 'Geometric packing'),
    Library('string', 'String manipulation')]

@app.route('/')
def index():
    return render_template('library_list.html', libraries=all_libraries)
    
@app.route('/favicon.ico')
def favicon():
    return ''

@app.route('/<library_name>')
def library_detail(library_name):
    library = parse_library(library_name)
    return render_template('library_detail.html', library=library)

@app.route('/<library_name>/<node_name>')
def node_detail(library_name, node_name):
    library = parse_library(library_name)
    node = library.find_node(node_name)
    return render_template('node_detail.html', library=library, node=node)

def parse_library(library_name):
    library = Library(library_name, '')
    et = ElementTree.parse(open(library.file))
    nodes = [Node.from_element(library, e) for e in et.find('node').findall('node')]
    library.nodes =  nodes
    return library

if __name__=='__main__':
    app.run(host='0.0.0.0', debug=True)
