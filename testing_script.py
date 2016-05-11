import os
import sys
from subprocess import call
from subprocess import check_output


"""
run on command line with "testing_script testdir"

Checks whether a lyrics file is empty, if so ignores the file.
If a lyrics file is missing a line (ie, there is a note but no lyric) the line is skipped in both the notes and lyrics files.
"""

if __name__=='__main__':
    testdir = sys.argv[1]

    """
    Creates 2 files in our data directory, one where each line is the lyrics of one song and another where each line
    contains the corresponding notes. The lyrics file is passed into hmm, and the notes file is used to evaluate the
    output of hmm.
    These files only need to be created once, so this code can be commented out if doing several tests in a row with
    the same song files.
    """
    with open(os.path.join(testdir, "compositeLyrics"), "w") as lyricsFile:
        with open(os.path.join(testdir, "compositeNotes"), "w") as notesFile:
            for filename in os.listdir(testdir):
                if "lyrics_edited" in filename:
                    print filename
                    with open(os.path.join(testdir, filename)) as lyricTestFile:
                        f = lyricTestFile.read().split("\n")
                        if len(f) > 1:
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
                                            syllables_list.append(lyric_line.split()[3])
                                            notes_list.append(notes[int(lyric_line.split("\t")[0])].split()[3])
                        notesFile.write(" ".join(notes_list) + "\n")
                    lyricsFile.write(" ".join(syllables_list) + "\n")

    """
    Call hmm on the lyrics file created above.
    """
    call("python hmm.py " + os.path.join(testdir, "compositeLyrics") + " models/music " + "v", shell=True)


    """
    Calculate and print the accuracy of our hmm compared to the actual notes of the songs.
    We add one to our count of correct notes for each note that is exactly correct, then divide by the
    total number of notes. These counts accumulate over all songs in our testing files.
    """
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
