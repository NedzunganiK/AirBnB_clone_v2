#!/user/bin/python3

"""
Fabric script based on the file 2-do_deploy_web_static.py that creates and
distributes an archive to the web servers.

Execute: fab -f 3-deploy_web_static.py deploy -i ~/.ssh/id_rsa -u ubuntu
"""

from fabric.api import env, local, put, run
from datetime import datetime
from os.path import exists, isdir

env.hosts = ['54.160.77.90', '100.25.190.21']

def do_pack():
    """Generates a tgz archive from the contents of the web_static folder."""
    try:
        date = datetime.now().strftime("%Y%m%d%H%M%S")
        if not isdir("versions"):
            local("mkdir versions")
        file_name = f"versions/web_static_{date}.tgz"
        local(f"tar -cvzf {file_name} web_static")
        return file_name
    except Exception as e:
        print(f"Packaging failed: {e}")
        return None

def do_deploy(archive_path):
    """Distributes an archive to the web servers."""
    if not exists(archive_path):
        return False

    try:
        file_name = archive_path.split("/")[-1]
        no_ext = file_name.split(".")[0]
        release_dir = "/data/web_static/releases/"
        tmp_path = f"/tmp/{file_name}"

        # Upload the archive to the /tmp/ directory on the server
        put(archive_path, tmp_path)

        # Create the directory to uncompress the archive
        run(f'mkdir -p {release_dir}{no_ext}/')

        # Uncompress the archive
        run(f'tar -xzf {tmp_path} -C {release_dir}{no_ext}/')

        # Remove the archive from the /tmp/ directory
        run(f'rm {tmp_path}')

        # Move contents out of the web_static directory
        run(f'mv {release_dir}{no_ext}/web_static/* {release_dir}{no_ext}/')
        run(f'rm -rf {release_dir}{no_ext}/web_static')

        # Delete the existing symbolic link
        run('rm -rf /data/web_static/current')

        # Create a new symbolic link
        run(f'ln -s {release_dir}{no_ext}/ /data/web_static/current')

        return True
    except Exception as e:
        print(f"Deployment failed: {e}")
        return False

def deploy():
    """Creates and distributes an archive to the web servers."""
    archive_path = do_pack()
    if archive_path is None:
        return False
    return do_deploy(archive_path)
