import os, sys
import time
import getopt

from dropbox import client, rest, session

###########################################################################
#   Simple dropbox backup script                                          #
#                                                                         #
#   License: Do what you want, see www.dropbox.com                        #
#                                                                         #
#   Get your own developer key at www.dropbox.com/developers              #
#   add to password.txt, first line APP_KEY, second line APP_SECRET       #
#                                                                         #
#   https://github.com/trondkla/dropbox-simple-backuper/                  #
#   Trond Klakken - trondkla
#                                                                         #
###########################################################################

APP_KEY, APP_SECRET = '', ''

lines = open('password.txt', 'rb').read().splitlines()
if len(lines) == 2:
    APP_KEY = lines[0]
    APP_SECRET = lines[1]

ACCESS_TYPE = 'app_folder'  # should be 'dropbox' or 'app_folder' as configured for your app

VERSION = "1.0"

class StoredSession(session.DropboxSession):
    """a wrapper around DropboxSession that stores a token to a file on disk"""
    TOKEN_FILE = "token_store.txt"

    def load_creds(self):
        try:
            stored_creds = open(self.TOKEN_FILE).read()
            self.set_token(*stored_creds.split('|'))
            return True
        except IOError:
            return False

    def write_creds(self, token):
        f = open(self.TOKEN_FILE, 'w')
        f.write("|".join([token.key, token.secret]))
        f.close()

    def delete_creds(self):
        os.unlink(self.TOKEN_FILE)

    def link(self):
        request_token = self.obtain_request_token()
        url = self.build_authorize_url(request_token)
        print "url:", url
        print "Please authorize in the browser. After you're done, press enter."
        raw_input()

        self.obtain_access_token(request_token)
        self.write_creds(self.token)

    def unlink(self):
        self.delete_creds()
        session.DropboxSession.unlink(self)

class Uploader():
    def __init__(self, app_key, app_secret, verbose=False):
        self.sess = StoredSession(app_key, app_secret, access_type=ACCESS_TYPE)
        self.api_client = client.DropboxClient(self.sess)
        self.verbose = verbose

        #Not logged in, show link
        if not self.sess.load_creds():
            self._link()

    def verboseprint(self, *args):
        if self.verbose:
            for arg in args:
               print arg,
            print

    def _link(self):
        """log in to a Dropbox account"""
        try:
            self.sess.link()
        except rest.ErrorResponse, e:
            print 'Error: %s\n' % str(e)

    def _unlink(self):
        """ Unlink app from Dropbox account """
        self.sess.unlink()
        print "Account unlinked"

    def get_metadata(self, file):
        """ Returns metadata for a file, or False if file not present """
        path = file

        try:
            return self.api_client.metadata( path ) 
        except:
            return False


    def upload(self, file_path, dropbox_path=None, overwrite=False, force=False):
        """ Uploads a file 
            - overwrite = False | Overwrites Dropbox file_path if time stamps different
            - force = False | flags overwrites file in Dropbox even when time stamp matches

        """


        if dropbox_path is None:
            file_path_as_list = file_path.split("/")
            dropbox_path = file_path_as_list[len(file_path_as_list)-1]

        file_to_be_updated = False

        if os.path.exists( file_path ):
            metadata = self.get_metadata( dropbox_path )

            # File exits on dropbox
            if metadata:

                # Overwrite file on dropbox
                if overwrite:
                    local_file_time_modified = time.localtime(os.path.getmtime(file_path))
                    dropbox_file_time_modified = time.strptime(metadata['modified'], "%a, %d %b %Y %H:%M:%S +0000")

                    # Has same timestamp do nothing
                    if (local_file_time_modified is dropbox_file_time_modified) and not force:
                        self.verboseprint( "Already synched" )
                    else:
                    # Has different timestamps or forced
                        if force:
                            self.verboseprint( "Forced" )
                        else:
                            self.verboseprint( "Differnt timestamp, synching")
                        file_to_be_updated = True
                else:
                    self.verboseprint( "File exists in dropbox, uploading as duplicate" )
                    file_to_be_updated = True

            else:
                self.verboseprint( "Uploading file, does not exists" )
                file_to_be_updated = True

        else:
            self.verboseprint( "File '%s' does not exist" % file_path )

        if file_to_be_updated:
            print "Starting file upload"
            from_file = open(os.path.expanduser(file_path), "rb")
            self.api_client.put_file(dropbox_path, from_file, overwrite=overwrite)
            print "File uploaded"

    def move(self, from_path, to_path):
        """ Moves a file on Dropbox, returns metadata if succes, False if not """
        metadata_from = self.get_metadata( from_path )

        if metadata_from:
            try:
                return self.api_client.file_move(from_path, to_path)
                print "Moved file from %s to %s" % (from_path, to_path)
            except:
                print "Error when moving, file may not exists"
                return False

    def delete(self, dropbox_path):
        """ Deletes file from dropbox. Returns boolean if deleted """
        try:
            self.api_client.file_delete(dropbox_path)
            print "Deleted file: %s" % dropbox_path
            return True
        except:
            print "File not found, or another error"
            return False

    def search(self, path, query):
    	""" Search for files in directory """
        try:
            return self.api_client.search(path, query)
        except:
            return None

def main():

    verbose, force, overwrite, unlink, delete, move = False, False, False, False, False, False

    def usage():
        use = [
            "-o, --overwrite  | Overwrite existing file in dropbox",
            "-f, --force      | Force when timestamp matches",
            "--unlink         | Unlink app from dropbox",
            "--move           | Move file on dropbox",
            "--delete         | Deletes file from dropbox",
                 ]

        print "Simple dropbox backuper - Version %s" % VERSION
        print "\n  usage: python %s -fov /path/to/file \n\n OPTIONS:" % sys.argv[0] 
        for u in use:
            print "   %s" % u

    if APP_KEY == '' or APP_SECRET == '':
        exit("You need to set your APP_KEY and APP_SECRET!")

    args = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h:fomv", ["help", "force", "overwrite", "unlink", "move", "delete"])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ("-v", "--verbose"):
            verbose = True
        elif o in ("-h", "--help"):
            usage()
            sys.exit()
        elif o in ("-f", "--force"):
            force = True
        elif o in ("-o", "--overwrite"):
            overwrite = True
        elif o == "--unlink":
            unlink = True
        elif o in ("-m", "--move"):
            move = True
        elif o == "--delete":
            delete = True
        else:
            assert False, "unhandled option"

    file_path = args[0] if len(args) in (1, 2) else None
    to_path = args[1] if len(args) == 2 else None

    if file_path or unlink:

        uploader = Uploader(APP_KEY, APP_SECRET, verbose=verbose)

        if unlink:
            uploader._unlink()
            sys.exit(0)

        if move:
            uploader.move(file_path, to_path)
            sys.exit(0)

        if delete:
            uploader.delete(file_path)
            sys.exit(0)

        uploader.upload(file_path, dropbox_path=to_path, force=force, overwrite=overwrite)
    else:
        usage()

if __name__ == '__main__':
    main()
