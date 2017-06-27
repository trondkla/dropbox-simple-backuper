dropbox-simple-backuper (DEPRECATED)
=======================

Uses dropbox API v1, which is deprecated: https://blogs.dropbox.com/developers/2016/06/api-v1-deprecated/

Simple python script for taking backups without having files synched (upload, move/rename and delete)

Backup files from your server without synching all files to your server

Max file size is 150 MB, this is a limit dropbox has set

------------------------------------------------------------------------

Install instructions: Go to www.dropbox.com/developers
Get a app key and secret, and the development kits. Follow installations

Can be installed through "easy_install dropbox" on a distro with python-setuptools

When you have the dropbox package in python and password.txt and token_store.txt you are ready

------------------------------------------------------------------------



Simple dropbox backuper - Version 1.0  

usage: python upload.py -fov /path/to/file  

OPTIONS:  
    -o, --overwrite  | Overwrite existing file in dropbox  
    -f, --force      | Force when timestamp matches  
    --unlink         | Unlink app from dropbox  
    --move           | Move file on dropbox  
    --delete         | Deletes file from dropbox  

