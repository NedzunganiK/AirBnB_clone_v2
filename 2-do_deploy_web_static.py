#!/usr/bin/python3
"""
Fabric script based on the file 1-pack_web_static.py that distributes an
archive to the web servers
"""

from fabric.api import put, run, env
from os.path import exists

env.hosts = ['54.89.109.87', '100.25.190.21']

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

