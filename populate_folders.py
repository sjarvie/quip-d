import quip
import os
from html2text import html2text
import codecs
import sys
import argparse


def parse_args(args):
    """Simple argument parser for the script"""
    parser = argparse.ArgumentParser(description='Populate local folders')
    parser.add_argument(
        '-t',
        '--token',
        type=str,
        help='Quip Access token')
    parser.add_argument(
        '-d',
        '--directory',
        type=str,
        help='Local Directory to sync into')

    parsed_args = parser.parse_args(args)
    return parsed_args



class LocalWriter(object):
    """
    Writing class for syncing Quip content to a local directory
    """
    def __init__(self, client, local_folder):
        self._client = client
        self._user = client.get_authenticated_user()
        self._local_folder = local_folder


    def write_folder(self, quip_folder_id, current_path):


        # TODO try/catch
        folder = self._client.get_folder(quip_folder_id)
        children = folder['children']

        for child in children:
            item_type = child.keys()[0]
            item_id = child.values()[0]

            # create new folder and recurse 
            if item_type == 'folder_id':
                folder_path = "%s/%s" % (current_path, item_id)

                # create folder
                if not os.path.exists(folder_path):
                        os.makedirs(folder_path)

                # recurse
                self.write_folder(item_id, folder_path)

            # write the thread in markdown format
            else:

                thread = self._client.get_thread(item_id)
                html = thread['html']
                title = thread['thread']['title']
                markdown = html2text(html)
                file_path = "%s/%s-%s" % (current_path, title, item_id)

                # create folder if need be
                if not os.path.exists(current_path):
                        os.makedirs(current_path)

                f = open(file_path, "w")
                f.write(markdown)
                f.close()

    def sync_folders(self):
        self.write_folder(self._user['desktop_folder_id'], self._local_folder)


import sys
import getopt

def main(args):
    args = parse_args(args)

    directory = args.directory
    token = args.token
    client = quip.QuipClient(access_token=token)

    writer = LocalWriter(client, directory)
    writer.sync_folders()

if __name__ == "__main__":
    main(sys.argv[1:])

