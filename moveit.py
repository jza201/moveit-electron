"""
GUI tool to create a Bag from a filesystem folder.
"""

import sys
import os
import shutil
import bagit
from time import strftime
from distutils.dir_util import copy_tree
import tempfile
import zerorpc


def generate_file_md5(zipname, blocksize=2**20):
    m = hashlib.md5()
    with open(zipname, "rb") as f:
        while True:
            buf = f.read(blocksize)
            if not buf:
                break
            m.update(buf)
    return m.hexdigest()


class MoveIt(object):
    def package(self, contactname, department, email, phone, creator, rrsda, title, datefrom, dateto, description, metadata, package_folder):
        print(contactname, department, email, phone, creator, rrsda, title, datefrom, dateto, description, metadata, package_folder)
        bag_dir_parent = tempfile.mkdtemp()
        if os.path.isdir(bag_dir_parent):
            shutil.rmtree(bag_dir_parent)
        bag_dir = os.path.join(bag_dir_parent, 'bag')
        os.makedirs(bag_dir)
        copy_tree(package_folder, bag_dir)

        try:
            bag = bagit.make_bag(bag_dir, None, 1, ['md5'])
            bag.info['Transfer Time'] = strftime("%Y-%m-%d %H:%M:%S")
            bag.info['Contact Name'] = contactname
            bag.info['Department'] = department
            bag.info['Email'] = email
            bag.info['Phone'] = phone
            bag.info['Record Creator'] = creator
            bag.info['RRSDA Number'] = rrsda
            bag.info['Transfer Title'] = title
            bag.info['Date Range'] = (datefrom + "-" + dateto)
            bag.info['Descrption'] = description
            bag.info['Other Metadata'] = metadata
            bag.save()
        except (bagit.BagError, Exception) as e:
            return False

        bag_destination = os.path.join(str(bag_dir_parent), (title))
        zipname = shutil.make_archive(bag_destination, 'zip', bag_dir)
        shutil.rmtree(bag_dir)

        desktopPath = os.path.expanduser("~/Desktop/")
        outputPath = desktopPath + os.path.splitext(os.path.basename(zipname))[0]
        os.mkdir(outputPath)
        shutil.move(zipname, os.path.join(outputPath, os.path.basename(zipname)))
        return True

if __name__ == '__main__':
    s = zerorpc.Server(MoveIt())
    s.bind('tcp://127.0.0.1:' + str(sys.argv[1]))
    s.run()