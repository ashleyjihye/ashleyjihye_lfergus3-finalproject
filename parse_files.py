import os, sys
import HTMLParser

__author__= 'Ashley Thomas and Leah Ferguson'

"""Run parser on commandline by doing 'parse_files input_directory'"""




if __name__=='__main__':
    inputdir = sys.argv[1]

    for filename in os.listdir(inputdir):
        if "notes" in filename or "lyrics" in filename:
            f = open(filename).read()
            l = f.split('/n')[2:]
            nested_list = []
            for line in l:
                nested_list.append(line.split())

            if "notes" in filename:
                #write new file
                f = open(filename.split('.')[0] + ".notes_edited.txt", "w")
                #change first note of song to start symbol "S"
                nested_list[0][3] = "S"
                f.write("\t".join(nested_list[0][:4]) + "/n")
                prev_octave = int(nested_list[0][4])
                prev_note = int(nested_list[0][3])
                for i in range(1, len(nested_list)):
                    interval = (int(nested_list[i][3]) - prev_note) + (12*(int(nested_list[i][4])-prev_octave))
                    f.write("\t".join(nested_list[i][:3] + "\t" + str(interval) + "\n"))
                    prev_octave = nested_list[i][4]
                    prev_note = nested_list[i][3]
            if "lyrics" in filename:
                #remove the punctuation from the lyrics
                for line in nested_list:
                    temp_str = line[3]
                    temp_str = HTMLParser.HTMLParser().unescape(temp_str)
                    out = "".join(c for c in temp_str if c not in ('!','.',':','\'','\"','?',';',',','(',')','-','_','[',']','/'))
                    line[3] = out



"""files:
    currently have: [note] [start] [end] [pitch] [octave]

    want: [note] [start] [end] [interval]
       keep the first line as the absolute note value, then change subsequent lines to the intervals
       """
