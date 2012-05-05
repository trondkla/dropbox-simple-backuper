dropbox-simple-backuper
=======================

Simple python script for taking backups without having files synched (upload, move/rename and delete)

Backup files from your server without synching all files to your server

------------------------------------------------------------------------

Install instructions: Go to www.dropbox.com/developers
Get a app key and secret, and the development kits. Follow installations

------------------------------------------------------------------------



Simple dropbox backuper - Version 1.0  

usage: python upload.py -fov /path/to/file  

OPTIONS:  
    -o, --overwrite  | Overwrite existing file in dropbox  
    -f, --force      | Force when timestamp matches  
    --unlink         | Unlink app from dropbox  
    --move           | Move file on dropbox  
    --delete         | Deletes file from dropbox  

