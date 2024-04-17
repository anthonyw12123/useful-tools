import os, datetime, errno, argparse, sys, glob
from pathlib import Path

def dir_path(string):
    print(string)
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)

def is_extension(string):
    if(not string):
        raise ValueError("extension must be provided")
    return string

def create_file_list(CWD):
    """ takes string as path, returns tuple(files,date) """

    if(not CWD): 
        raise Exception("supplied path is not a value")
    files_with_mtime = []
    files = glob.glob(CWD + "*" + ext)
    for filename in [f for f in files]:
        files_with_mtime.append((filename,datetime.datetime.fromtimestamp(os.stat(filename).st_mtime).strftime('%Y-%m-%d')))
    return files_with_mtime

def create_directories(target, files):
    """ takes tuple(file,date) from create_file_list() """

    m = []
    for i in files:
        m.append(i[1])
    for i in set(m):
        try:
            os.makedirs(os.path.join(target,i))
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

def move_files_to_folders(target, files):
    """ gets tuple(file,date) from create_file_list() """
    for i in files:
        try:
            print("moving " + i[0] + " to " + os.path.join(target,(i[1] + '/' + os.path.basename(i[0]))))
            os.rename(i[0], os.path.join(target,(i[1] + '/' + os.path.basename(i[0]))))
        except Exception as e:
            raise
    return len(files)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog=sys.argv[0], usage='%(prog)s [options]')
    parser.add_argument("-t", "--target", type=dir_path,help="Target directory", required=True)
    parser.add_argument("-e","--extension",type=is_extension,help="File extensions to match",required=True)
    parser.add_argument("-v","--verbose",default=False,required=False)
    args = parser.parse_args()

    ext =  '.' + args.extension
    files = create_file_list(args.target)
    create_directories(args.target, files)
    print("Moved %i files" % move_files_to_folders(args.target, files))
