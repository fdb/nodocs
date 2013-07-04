import os.path

project_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = '/www/nodocs.nodebox.net/nodocs'
activate_this = os.path.join(project_dir, 'bin', 'activate_this.py')

execfile(activate_this, dict(__file__=activate_this))

import sys
sys.path.append(project_dir)

from nodocs import app as application