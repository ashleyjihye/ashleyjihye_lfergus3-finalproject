import os
import sys
from subprocess import call
from subprocess import check_output

"""
fix:
    line after blank (tried making it > instead of >=, broke stuff (the lyrics after a break were missing))

"""

# run with "testing_script testdir"

if __name__=='__main__':
    testdir = sys.argv[1]

    """
    #use this dict to keep track of whether a song has a lyrics_edited file, ie, whether the song has lyrics
    lyric_dict = {}JC

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
            if "notes[Ma7L_edited" in filename:
                if filename.split(".")[0] in lyric_dict:
                    print filename
                    with open(os.path.join(testdir, filename)) as testFile:
                        f = testFile.read().split("\n")
                        notes_list = []
                        for line in f:
                            if len(line.split()) == 4:
                                notes_list.append(line.split()[3])
                    notesFile.write(" ".join(notes_list) + "\n")
    """

    #use this dict to keep track of whether a song has a lyrics_edited file, ie, whether the song has lyrics

    #create a file where each line is the entire lyrics of one testing file
    with open(os.path.join(testdir, "compositeLyrics"), "w") as lyricsFile:
        with open(os.path.join(testdir, "compositeNotes"), "w") as notesFile:
            for filename in os.listdir(testdir):
                if "lyrics_edited" in filename:
                    print filename
                    with open(os.path.join(testdir, filename)) as lyricTestFile:
                        f = lyricTestFile.read().split("\n")
                        syllables_list = []
                        notes_list = []
                        prev_note = 0
                        for i, lyric_line in enumerate(f):
                            with open(os.path.join(testdir, (filename.split(".")[0]+".notes_edited.txt"))) as notesTestFile:
                                notes = notesTestFile.read().split("\n")
                                if (len(lyric_line.split()) == 4) and (len(notes[int(lyric_line.split("\t")[0])].split("\t")) == 4):
                                    if int(lyric_line.split()[0]) == (prev_note + 1):
                                        syllables_list.append(lyric_line.split()[3])
                                        notes_list.append(notes[int(lyric_line.split("\t")[0])].split()[3])
                                        prev_note += 1
                                    else:
                                        #deal with notes that have no lyric
                                        while (int(lyric_line.split()[0]) >= (prev_note + 1)):
                                            prev_note += 1
                        notesFile.write(" ".join(notes_list) + "\n")
                    lyricsFile.write(" ".join(syllables_list) + "\n")

    """
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
    """
