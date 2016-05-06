import os
import sys
from subprocess import call


"""
need to do:
    create a lyric file from each test song
    run program on each test lyric file
    compare -->
"""

# run with "testing_script testdir"

if __name__=='__main__':
    testdir = sys.argv[1]

    #create a file where each line is the entire lyrics of one testing file
    with open(os.path.join(testdir, "_compositeLyrics"), "w") as lyricsFile:
        for filename in os.listdir(testdir):
            print filename
            if "lyrics_edited" in filename:
                with open(os.path.join(testdir, filename)) as testFile:
                    f = testFile.read().split("\n")
                    syllables_list = []
                    prev_note = 0
                    for line in f:
                        if len(line.split()) == 4:
                            if int(line.split()[0]) == (prev_note + 1):
                                syllables_list.append(line.split()[3])
                                prev_note += 1
                            else:
                                #print "here 2"
                                syllables_list.append("<UNK>")
                                prev_note += 1


                lyricsFile.write(" ".join(syllables_list) + "\n")

    #create a file where each line is all the notes of one testing file
    with open(os.path.join(testdir, "_compositeNotes"), "w") as notesFile:
        for filename in os.listdir(testdir):
            if "notes_edited" in filename:
                with open(os.path.join(testdir, filename)) as testFile:
                    f = testFile.read().split("\n")
                    notes_list = []
                    for line in f:
                        notes_list.append(line.split()[3])
                notesFile.write(" ".join(syllables_list) + "\n")

    #subprocess.call("python hmm.py " + os.path.join(testdir, "_compositeLyrics") + " models/music " + "v")


"""
fix all the <UNK> values!!
fix placement of new files? (not in same directory as data)
why is musicxml.mat in the data directory?
test whether a song has lyrics
how does it know when to stop?

call HMM
compare created notes file to generated file
"""
