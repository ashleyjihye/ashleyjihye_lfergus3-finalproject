import os
import sys
from subprocess import call
from subprocess import check_output

"""
song 24 lyrics edited "2so" key error in hmm.py --> problem with data??

how to deal with <UNK> at the end of the lyrics
(currently not every note in compositeNotes has a corresponding lyric in compositeLyrics)

a file doesn't have a lyrics_edited if it has no lyrics, right?
"""

# run with "testing_script testdir"

if __name__=='__main__':
    testdir = sys.argv[1]

    #use this dict to keep track of whether a song has a lyrics_edited file, ie, whether the song has lyrics
    lyric_dict = {}

    #create a file where each line is the entire lyrics of one testing file
    with open(os.path.join(testdir, "compositeLyrics"), "w") as lyricsFile:
        for filename in os.listdir(testdir):
            if "lyrics_edited" in filename:
                lyric_dict[filename.split(".")[0]] = filename
                print filename
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
                                #deal with notes that have no lyric
                                while (int(line.split()[0]) > (prev_note + 1)):
                                    syllables_list.append("<UNK>")
                                    prev_note += 1
                                syllables_list.append(line.split()[3])
                                prev_note += 1


                lyricsFile.write(" ".join(syllables_list) + "\n")

    #create a file where each line is all the notes of one testing file
    with open(os.path.join(testdir, "compositeNotes"), "w") as notesFile:
        for filename in os.listdir(testdir):
            if "notes_edited" in filename:
                if filename.split(".")[0] in lyric_dict:
                    print filename
                    with open(os.path.join(testdir, filename)) as testFile:
                        f = testFile.read().split("\n")
                        notes_list = []
                        for line in f:
                            if len(line.split()) == 4:
                                notes_list.append(line.split()[3])
                    notesFile.write(" ".join(notes_list) + "\n")

    #print check_output("python hmm.py " + os.path.join(testdir, "compositeLyrics") + " models/music " + "v", shell=True)
    call("python hmm.py " + os.path.join(testdir, "compositeLyrics") + " models/music " + "v", shell=True)

    #compare compsiteLyrics.tagged with compositeNotes
    #keep track of how many notes (accumulate over all files)
    #keep track of accuracy: for each note, if correct +1, if incorrect stays same
    #divide accuracy by total notes
    #print accuracy

    total_notes = 0
    correct_notes = 0
    with open(os.path.join(testdir, "compositeNotes")) as gold:
        with open(os.path.join(testdir, "compositeLyrics.tagged")) as tagged:
            gold_lines = gold.read().split("\n")
            tagged_lines = tagged.read().split("\n")
            for i, line in enumerate(gold_lines):
                g_l = line.split(" ")
                t_l = tagged_lines[1].split(" ")
                for j, n in enumerate(g_l):
                    total_notes += 1
                    if (len(t_l) > j):
                        if (n == t_l[j]):
                            correct_notes += 1
                    else:
                        continue
    accuracy = correct_notes/(float(total_notes))
    print "The accuracy is: " + str(accuracy)
