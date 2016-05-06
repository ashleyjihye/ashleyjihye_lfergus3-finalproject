import os, sys
import HTMLParser
from collections import defaultdict

__author__= 'Ashley Thomas and Leah Ferguson'

"""Run parser on commandline by doing 'parse_files input_directory'"""

def normalize(countdict):
    """given a dictionary mapping items to counts,
    return a dictionary mapping items to their normalized (relative) counts
    Example: normalize({'a': 2, 'b': 1, 'c': 1}) -> {'a': 0.5, 'b': 0.25, 'c': 0.25}
    """
    # Do not modify this function
    total = sum(countdict.values())
    return {item: val/total for item, val in countdict.items()}



if __name__=='__main__':
    inputdir = sys.argv[1]

    for filename in os.listdir(inputdir):
        if "notes.txt" in filename or "lyrics.txt" in filename:
            with open(os.path.join(inputdir,filename)) as theFile:
                f = theFile.read()

                f = f.lower()
                l = f.split('\n')[2:]
                if l == [''] or l == []:
                    continue
                nested_list = []
                for line in l:
                    if line != "":
                        nested_list.append(line.split())

            if "notes.txt" in filename:
                #write new file
                f = open(os.path.join(inputdir,filename.split('.')[0] + ".notes_edited.txt"), "w")
                f.write("0\t0\t0\t" + "#" + "\n")
                f.write("\t".join(nested_list[0][:4]) + "\n")
                prev_octave = int(nested_list[0][4])
                prev_note = int(nested_list[0][3])
                for i in range(1, len(nested_list)):
                    interval = (int(nested_list[i][3]) - prev_note) + (12*(int(nested_list[i][4])-prev_octave))
                    f.write("\t".join(nested_list[i][:3]) + "\t" + str(interval) + "\n")
                    prev_octave = int(nested_list[i][4])
                    prev_note = int(nested_list[i][3])
                f.close()
            if "lyrics.txt" in filename:
                f = open(os.path.join(inputdir,filename.split('.')[0] + ".lyrics_edited.txt"), "w")
                #remove the punctuation from the lyrics
                for i,line in enumerate(nested_list):
                    if len(line) > 3:
                        temp_str = line[3]
                        temp_str = HTMLParser.HTMLParser().unescape(temp_str)
                        out = "".join(c for c in temp_str if c not in ('!','.',':','\'','\"','?',';',',','(',')','-','_','[',']','/'))
                        if out != "":
                            f.write("\t".join(nested_list[i][:3]) + "\t" + out + "\n")
                f.close()



    emitcounts = defaultdict(lambda : defaultdict(float))
    transcounts = defaultdict(lambda : defaultdict(float))
    for filename in os.listdir(inputdir):
        if "notes_edited.txt" in filename:

            notes_f = open(os.path.join(inputdir,filename)).read()
            
            notes = notes_f.split('\n')
            notes_list = []
            for line in notes:
                if line != "":
                    notes_list.append(line.split())

            #build the transitions dict
            for i in range(0,len(notes_list)-1):
                current_interval = notes_list[i][3]
                next_interval = notes_list[i+1][3]
                transcounts[current_interval][next_interval] += 1

            try:
                lyrics_f = open(os.path.join(inputdir,filename.split('.')[0] + ".lyrics_edited.txt")).read()
            except IOError:
                print('There was an error opening' + filename.split('.')[0] + ".lyrics_edited.txt")
                continue

            lyrics = lyrics_f.split('\n')
            lyrics_list = []
            for line in lyrics:
                if line != "":
                    lyrics_list.append(line.split())

            #build the emissions dict
            note_counter = 0
            for i in range(0, len(lyrics_list)-1):
                corresponding_note = lyrics_list[i][0]

                while (notes_list[note_counter][0] != corresponding_note):
                    if notes_list[note_counter][3] != "#":
                        emitcounts[notes_list[note_counter][3]]["<UNK>"] += 1
                    note_counter += 1

                emitcounts[notes_list[note_counter][3]][lyrics_list[i][3]] += 1


            """
            lyric_counter = 0
            for i in range(0,len(notes_list)-1):
                current_interval = notes_list[i][3]
                if len(lyrics_list) > lyric_counter:
                    note_for_lyric = int(lyrics_list[lyric_counter][0])
                    if note_for_lyric == (i+1):
                        current_lyric = lyrics_list[lyric_counter][3]
                        lyric_counter += 1
                        emitcounts[current_interval][current_lyric] += 1
                    else:
                        emitcounts[current_interval]["<UNK>"] += 1
                else:
                    emitcounts[current_interval]["<UNK>"] += 1
            """


    """
    emissions = {}
    for k, v in emitcounts.iteritems():
        emissions[k] = normalize(v)

    transitions = {}
    for k, v in transcounts.iteritems():
        transitions[k] = normalize(v)


    #write emissions to file
    f = open("models/music.emit", "w")
    for k, v in emissions.iteritems():
        for k1, v1 in v.iteritems():
            f.write(k + " " + k1 + " " + str(v1) + "\n")

    f.close()


    #write transitions to file
    f = open("models/music.trans", "w")
    for k, v in transitions.iteritems():
        for k1, v1 in v.iteritems():
            f.write(k + " " + k1 + " " + str(v1) + "\n")

    f.close()
    """


    #write emissions to file
    f = open("models/music.emit", "w")
    for k, v in emitcounts.iteritems():
        for k1, v1 in v.iteritems():
            f.write(k + " " + k1 + " " + str(v1) + "\n")

    f.close()


    #write transitions to file
    f = open("models/music.trans", "w")
    for k, v in transcounts.iteritems():
        for k1, v1 in v.iteritems():
            f.write(k + " " + k1 + " " + str(v1) + "\n")

    f.close()













