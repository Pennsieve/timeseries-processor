
import os
import tarfile
import fnmatch
import shutil

def extract_directory(fname):
    directory = os.path.abspath(os.path.dirname(fname))
    tar = tarfile.open(fname)
    tar.extractall(directory)
    tar.close()
    return directory

def find_mefd(directory):
    mefd_files = []
    for tmpsess in os.listdir(directory):
        if tmpsess.endswith(".mefd") and not tmpsess.startswith('.'):
            mefd_files.append(os.path.join(directory,tmpsess))
    return mefd_files

def extract_all(mefd_session):
	pattern='*.gz'
	for root, dirs, files in os.walk(mefd_session):
	    for filename in fnmatch.filter(files, pattern):
	        if not filename.startswith('.'):
	            print(os.path.join(root, filename))
	            inF = gzip.open(os.path.join(root, filename), 'rb')
	            outF = open(os.path.join(root, os.path.splitext(filename)[0]), 'wb')
	            outF.write(inF.read())
	            inF.close()
	            outF.close()

def clean(mefd_session):
	shutil.rmtree(mefd_session)
