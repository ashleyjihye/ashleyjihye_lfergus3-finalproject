from random import randint
import os
import sys
import shutil
import glob

if __name__=='__main__':
    inputdir = sys.argv[1]
    num_test = int(sys.argv[2])

    files_to_delete = glob.glob(os.path.join(inputdir, "test/*"))
    for f in files_to_delete:
        os.remove(f)

    files_to_delete = glob.glob(os.path.join(inputdir, "train/*"))
    for f in files_to_delete:
        os.remove(f)

    current_num = 0

    test_files = {}

    while current_num < num_test:
        filenum = randint(1,5042)
        filenum = str(filenum).zfill(3)

        if os.path.isfile(os.path.join(inputdir, filenum + ".lyrics_edited.txt")) and (filenum not in test_files):
            files_to_copy = glob.iglob(os.path.join(inputdir, filenum + ".*"))
            i = 0
            for file_to_copy in files_to_copy:
                shutil.copy2(file_to_copy, os.path.join(inputdir, "test"))
                i += 1
            current_num += 1
            test_files[filenum] = filenum

    for filename in os.listdir(inputdir):
        file_array = filename.split(".")
        if len(file_array) > 2 and file_array[0] not in test_files and file_array[2] == "txt":
            shutil.copy2(os.path.join(inputdir, filename), os.path.join(inputdir, "train"))








