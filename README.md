Nodocs is a NodeBox node documentation generator. It's home is at http://nodocs.nodebox.net/

It takes a folder with node libraries and generates documentation for them automatically.

Running nodocs
==============
Nodocs requires nodebox to install in the same parent directory. So the organization would look like this:

    Projects/
        nodebox/
        nodocs/

Furthermore, the nodebox project needs the correct branch to be checked out. Currently, this is `javascript-export`.

To set up this directory structure, from the `Projects` directory, do:

    git clone https://github.com/nodebox/nodebox.git
    git clone https://github.com/fdb/nodocs.git
    cd nodebox
    git checkout javascript-export

To run the server, execute the following commands in the terminal:

    sudo easy_install virtualenv
    cd nodocs
    virtualenv .
    source bin/activate
    pip install -r requirements.txt 
    python nodocs.py

This will run a server on http://0.0.0.0:5000/ .
