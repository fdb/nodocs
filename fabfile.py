from fabric.api import env, run, cd

env.hosts = ['root@nodocs.nodebox.net']

def update():
    nodebox_dir = '/www/nodocs.nodebox.net/nodebox'
    with cd(nodebox_dir):
        run('git pull')
        run('touch ../nodocs/nodocs.wsgi')

def deploy():

    project_dir = '/www/nodocs.nodebox.net/nodocs'
    with cd(project_dir):
        run('git pull')
        run('touch nodocs.wsgi')

def all():
    update()
    deploy()

