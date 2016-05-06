"""Hidden Markov Model Toolkit
with the fundamental tasks --
randomly generating data,
finding the best state sequence for observation,
computing the probability of observations,
and Baum-Welch EM algorithm for parameter learning.
"""

__author__='Sravana Reddy'

import math
import numpy   # install this with pip or Canopy's package manager. You're probably all set if you have NLTK/matplotlib.
import numpy.random
import argparse
import codecs
import os
from collections import defaultdict

def normalize(countdict):
    """given a dictionary mapping items to counts,
    return a dictionary mapping items to their normalized (relative) counts
    Example: normalize({'a': 2, 'b': 1, 'c': 1}) -> {'a': 0.5, 'b': 0.25, 'c': 0.25}
    """
    # Do not modify this function
    total = sum(countdict.values())
    return {item: val/total for item, val in countdict.items()}

def read_arcs(filename):
    """Load parameters from file and store in nested dictionary.
    Assume probabilities are already normalized.
    Return dictionary and boolean indicating whether probabilities were provided.
    """
    # Do not modify this function
    arcs = {}
    provided = True
    for line in map(lambda line: line.split(), codecs.open(filename, 'r', 'utf8')):
        if len(line)<=2 or len(line) > 3:
            continue
        from_s = line[0]
        to_s = line[1]
        if len(line)==3:
            prob = float(line[2])
        else:
            prob = None
            provided = False
        if from_s in arcs:
            arcs[from_s][to_s] = prob
        else:
            arcs[from_s] = {to_s: prob}
    return arcs, provided

def write_arcs(arcdict, filename):
    """write dictionary of conditional probabilities to file
    """
    # Do not modify this function
    o = codecs.open(filename, 'w', 'utf8')
    for from_s in arcdict:
        for to_s in arcdict[from_s]:
            o.write(from_s+' '+to_s+' '+str(arcdict[from_s][to_s])+'\n')
    o.close()

def read_corpus(filename):
    # Do not modify this function
    return filter(lambda line: len(line)>0, map(lambda line: line.split(),
               codecs.open(filename, 'r', 'utf8').readlines()))

def sample_from_dist(d):
    """given a dictionary representing a discrete probability distribution
    (keys are atomic outcomes, values are probabilities)
    sample a key according to the distribution.
    Example: if d is {'H': 0.7, 'T': 0.3}, 'H' should be returned about 0.7 of time.
    """
    # Do not modify this function
    roll = numpy.random.random()
    cumul = 0
    for k in d:
        cumul += d[k]
        if roll < cumul:
            return k

class HMM:
    def __init__(self, transfile, emitfile, translock=False, emitlock=False, parse_input=True):
        """reads HMM structure from transition and emission files, and probabilities if given.
        no error checking: assumes the files are in the correct format."""
        # Do not modify this function
        self.transitions, tprovided = read_arcs(transfile)
        self.emissions, eprovided = read_arcs(emitfile)
        self.states = self.emissions.keys()

        self.translock = translock
        self.emitlock = emitlock
        self.parse_input =parse_input 

        # initialize with random parameters if probs were not specified
        if not tprovided:   # at least one transition probability not given in file
            print 'Transition probabilities not given: initializing randomly.'
            self.init_transitions_random()
        if not eprovided:   # at least one emission probability not given in file
            print 'Emission probabilities not given: initializing randomly.'
            self.init_emissions_random()

        #adding rest of transitions
        intervals = list(self.transitions.keys())
        for key in self.transitions:
            for k1 in self.transitions[key]:
                if k1 not in intervals:
                    intervals.append(k1)

        old_intervals = list(self.transitions.keys())
        for interval in intervals:
            if interval not in old_intervals:
                self.transitions[interval] = {}

        for key in self.transitions:
            existing_keys = list(self.transitions[key].keys())

            for interval in intervals:
                if interval != "#":
                    if interval not in existing_keys:
                        self.transitions[key][interval] = 1
                    else:
                        self.transitions[key][interval] += 1

        #adding rest of emissions
        all_words = []

        for key in self.emissions:
            words = list(self.emissions[key].keys())

            for word in words:
                if word not in all_words:
                    all_words.append(word)

        emission_keys = list(self.emissions.keys())
        for interval in intervals:
            if interval not in emission_keys and interval != "#":
                self.emissions[interval] = {}

        for key in self.emissions:
            for word in all_words:
                if word not in self.emissions[key]:
                    self.emissions[key][word] = 1
                else:
                    self.emissions[key][word] += 1


        emissions = {}
        for k, v in self.emissions.iteritems():
            emissions[k] = normalize(v)

        self.emissions = emissions

        transitions = {}
        for k, v in self.transitions.iteritems():
            transitions[k] = normalize(v)

        self.transitions = transitions 

    def init_transitions_random(self):
        """assign random probability values to the HMM transition parameters
        """
        # Do not modify this function
        for from_state in self.transitions:
            random_probs = numpy.random.random(len(self.transitions[from_state]))
            total = sum(random_probs)
            for to_index, to_state in enumerate(self.transitions[from_state]):
                self.transitions[from_state][to_state] = random_probs[to_index]/total

    def init_emissions_random(self):
        for state in self.emissions:
            random_probs = numpy.random.random(len(self.emissions[state]))
            total = sum(random_probs)
            for symi, sym in enumerate(self.emissions[state]):
                self.emissions[state][sym] = random_probs[symi]/total

    def generate(self, n):
        """return a list of n symbols by randomly sampling from this HMM.
        """
        # TODO: fill in
        # due at checkpoint date (ungraded)
        # Use the sample_from_dist helper function in this file
        generated = []
        for i in range(n):
            if i==0:
                state = sample_from_dist(self.transitions['#'])
            else:
                state = sample_from_dist(self.transitions[state])  # 'state' was generated last time
            symbol = sample_from_dist(self.emissions[state])
            generated.append(symbol)
        return generated

    def viterbi(self, observation):
        """given an observation as a list of symbols,
        compute and return the most likely state sequence that generated it
        using the Viterbi algorithm
        """
        transition_damper = .1
        viterbi_path = []

        viterbi_costs = numpy.zeros((len(self.states), len(observation)))
        viterbi_backpointers = numpy.zeros((len(self.states), len(observation)), dtype=int)

        for oi, obs in enumerate(observation):
            for si, state in enumerate(self.states):
                if oi==0:
                    viterbi_costs[si, oi] = math.pow(self.transitions['#'][state], transition_damper) * self.emissions[state][obs]
                else:
                    best_costs = {}
                    for pi, prevstate in enumerate(self.states):
                        best_costs[pi] = viterbi_costs[pi, oi-1] * math.pow(self.transitions[prevstate][state], transition_damper)

                    best_state, best_cost = max(best_costs.items(), key=lambda (state, cost): cost)
                    viterbi_costs[si, oi] =  best_cost * self.emissions[state][obs]
                    viterbi_backpointers[si, oi] = best_state

        oi = len(observation)-1
        best_state = numpy.argmax(viterbi_costs[:, oi])
        viterbi_path.append(self.states[best_state])
        while oi>0:
            best_state = viterbi_backpointers[best_state, oi]
            viterbi_path.append(self.states[best_state])
            oi-=1

        return viterbi_path[::-1]

    def forward(self, observation):
        """given an observation as a list of T symbols,
        compute and return the forward algorithm dynamic programming matrix
        of size m x T where m is the number of states.
        """
        # Do not modify this function
        forward_matrix = numpy.zeros((len(self.states), len(observation)))

        for oi, obs in enumerate(observation):
            for si, state in enumerate(self.states):
                if oi==0:
                    forward_matrix[si, oi] = self.transitions['#'][state] * self.emissions[state][obs]
                else:
                    for pi, prevstate in enumerate(self.states):
                        forward_matrix[si, oi] += forward_matrix[pi, oi-1] * self.transitions[prevstate][state]

                    forward_matrix[si, oi] *= self.emissions[state][obs]  # factor out common emission prob

        return forward_matrix

    def forward_probability(self, observation):
        """return probability of observation, computed with forward algorithm.
        """
        # Do not modify this function
        forward_matrix = self.forward(observation)
        # sum of forward probabilities in last time step, over all states
        return sum(forward_matrix[:, len(observation)-1])

    def backward(self, observation):
        """given an observation as a list of T symbols,
        compute and return the backward algorithm dynamic programming matrix
        of size m x T where m is the number of states.
        """
        # TODO: fill in
        # due at checkpoint date (ungraded)
        # Follow the example in the slides from Mar 07 as a guideline.
        backward_matrix = numpy.zeros((len(self.states), len(observation)))
        for si, state in enumerate(self.states):
            backward_matrix[si, len(observation)-1] = 1  # 1s in last column

        for oi in range(len(observation)-2, -1, -1):
            for si, state in enumerate(self.states):
                for ni, nextstate in enumerate(self.states):
                    backward_matrix[si, oi] += backward_matrix[ni, oi+1] * self.transitions[state][nextstate] * self.emissions[nextstate][observation[oi+1]]

        return backward_matrix

    def backward_probability(self, observation):
        """return probability of observation, computed with backward algorithm.
        """
        # Do not modify this function
        backward_matrix = self.backward(observation)
        backprob = 0.0  # total probability
        for si, state in enumerate(self.states):
            # prob of transitioning from # to state and giving out observation[0]
            backprob += self.transitions['#'][state] * self.emissions[state][observation[0]] * backward_matrix[si, 0]
        return backprob

    def maximization(self, emitcounts, transcounts):
        """M-Step: set self.emissions and self.transitions
        conditional probability parameters to be the normalized
        counts from emitcounts and transcounts respectively.
        Do not update if self.emissions if the self.emitlock flag is True,
        or self.transitions if self.translock is True.
        """
        # TODO: fill in
        # note that this is a short and simple function
        if not self.translock:
            for from_state in self.transitions:
                self.transitions[from_state] = normalize(transcounts[from_state])

        if not self.emitlock:
            for state in self.emissions:
                self.emissions[state] = normalize(emitcounts[state])

    def expectation(self, corpus):
        """E-Step: given a corpus, which is a list of observations,
        calculate the expected number of each transition and emission,
        as well as the log likelihood of the observations under the current parameters.
        return a list with the log likelihood, expected emission counts, and expected transition counts.
        """
        # TODO: fill in
        # follow the Excel sheet example and slides from Mar 10 to fully understand the E step

        log_likelihood = 0.0  # holds running total of the log likelihood of all observations
        emitcounts = defaultdict(lambda : defaultdict(float))  # expected emission counts
        transcounts = defaultdict(lambda : defaultdict(float)) # expected transition counts

        for observation in corpus:
            forward_matrix = self.forward(observation)
            backward_matrix = self.backward(observation)
            forward_prob = sum(forward_matrix[:, len(observation)-1])
            for oi, obs in enumerate(observation):
                #emission soft counts
                prob_state = {}
                for si, state in enumerate(self.states):
                    emitcounts[state][obs] += forward_matrix[si, oi] * backward_matrix[si, oi] / forward_prob
                #transition soft counts
                prob_state1_state2 = {}
                for si, state in enumerate(self.states):
                    if oi==0:
                        transcounts['#'][state] += forward_matrix[si, oi] * backward_matrix[si, oi] / forward_prob
                    else:
                        for pi, prevstate in enumerate(self.states):
                            transcounts[prevstate][state] += forward_matrix[pi, oi-1] * self.transitions[prevstate][state] * self.emissions[state][obs] * backward_matrix[si, oi] / forward_prob

            log_likelihood += numpy.log2(forward_prob)

        return log_likelihood, emitcounts, transcounts

    def expectation_maximization(self, corpus, convergence):
        """given a corpus,
        apply EM to learn the HMM parameters that maximize the corpus likelihood.
        stop when the log likelihood changes less than the convergence threhshold,
        and return the final log likelihood.
        """
        # Do not modify this function
        old_ll = -10**210    # approximation to negative infinity
        log_likelihood = -10**209   # higher than old_ll

        while log_likelihood-old_ll > convergence:
            old_ll = log_likelihood
            log_likelihood, emitcounts, transcounts = self.expectation(corpus) # E Step
            self.maximization(emitcounts, transcounts)  # M Step
            print 'LOG LIKELIHOOD:', log_likelihood,
            print 'DIFFERENCE:', log_likelihood-old_ll
        print 'CONVERGED'

        return log_likelihood

#return a list of syllables in a given sentence (in string form)
def syllables_from_sentence(syllable_dict, sentence):
    syllable_list = []

    sentence = sentence.lower()
    sentence = sentence.split(" ")

    for i in range(0, len(sentence)):
        if sentence[i] == "$":
            print "$ was in text"
            sentence[i] = "<UNK>"

    for word in sentence:
        if word not in syllable_dict or word == "<UNK>":
            print "The word " + word + " was not in our dictionary, so we're transforming it to an unknown word <UNK>"
            syllable_list += ["<UNK>"]
        else:
            syllable_list += syllable_dict[word]

    return syllable_list

#make the syllable dictionary (pairings of words and their corresponding syllables)
def make_dict(filename):

    syllables = {}

    with open(filename) as theFile:
        f = theFile.read()
        f = f.lower()
        f = f.replace('\r','\n')
        lines = f.split("\n")

        for line in lines:
            if line != "":
                line = line.split('\\')

                if line[1] not in syllables and len(line[1].split()) == 1:
                    syllables[line[1]] = line[-1].split("-")

    return syllables

#output the results of viterbi (ie. the intervals) into a score and a midi format
def show_output(corpusfile, corpus, score_app, midi_app):
    with open(corpusfile.split()[0] + '.tagged') as theFile:
        f = theFile.read().split('\n')


        """
        interval = (int(nested_list[i][3]) - prev_note) + (12*(int(nested_list[i][4])-prev_octave))
        """




def main():
    # Do not modify this function
    parser = argparse.ArgumentParser()
    # required arguments
    parser.add_argument('corpusfile', type=str, help='corpus of observations')
    parser.add_argument('paramfile', type=str, help='basename of the HMM parameter file')
    parser.add_argument('function',
                        type=str,
                        choices = ['v', 'p', 'em', 'g'],
                        help='best state sequence (v), total probability of observations (p), parameter learning (em), or random generation (g)?')
    # optional arguments for EM
    parser.add_argument('--convergence', type=float, default=0.1, help='convergence threshold for EM')
    parser.add_argument('--restarts', type=int, default=0, help='number of random restarts for EM')
    parser.add_argument('--translock', type=bool, default=False, help='should the transition parameters be frozen during EM training?')
    parser.add_argument('--emitlock', type=bool, default=False, help='should the emission parameters be frozen during EM training?')
    parser.add_argument('--parse_input', type=bool, default=False, help='parse the data into syllables (if it is currently in word format)')
    parser.add_argument('--show_output', type=bool, default=False, help='show calculated intervals as piece and as midi file')
    parser.add_argument('--score_app', type=str, default=None, help='which app to use to open up note score')
    parser.add_argument('--midi_app', type=str, default=None, help='which app to use to open up midi sound file')

    args = parser.parse_args()

    # initialize model and read data
    model = HMM(args.paramfile+'.trans', args.paramfile+'.emit', args.translock, args.emitlock, args.parse_input)

    if args.function == 'v':
        corpus = []
        if args.parse_input:
            syllable_dict = make_dict("eow.cd")
            with open(args.corpusfile) as theFile:
                f = theFile.read()
                f = f.split('\n')

                for i in range(0, len(f)):
                    if f[i] != "":
                        corpus.append(syllables_from_sentence(syllable_dict, f[i]))

        else:
            corpus = read_corpus(args.corpusfile)

        outputfile = os.path.splitext(args.corpusfile)[0]+'.tagged'
        with codecs.open(outputfile, 'w', 'utf8') as o:
            for observation in corpus:
                viterbi_path = model.viterbi(observation)
                o.write(' '.join(viterbi_path)+'\n')

        if args.show_output:
            show_output(corpusfile, corpus, args.score_app, args.midi_app)


    elif args.function == 'p':
        corpus = read_corpus(args.corpusfile)
        outputfile = os.path.splitext(args.corpusfile)[0]+'.dataprob'
        with open(outputfile, 'w') as o:
            for observation in corpus:
                o.write(str(model.backward_probability(observation))+'\n')

    elif args.function == 'em':
        corpus = read_corpus(args.corpusfile)

        # keep track of the parameters that maximize the log likelihood over different initializations
        best_log_likelihood = model.expectation_maximization(corpus, args.convergence)
        best_transitions = model.transitions
        best_emissions = model.emissions

        #restart and run EM with random initializations
        for restart in range(args.restarts):
            print "RESTART", restart+1, 'of', args.restarts
            if not model.translock:
                model.init_transitions_random()
                print 'Re-initializing transition probabilities'
            if not model.emitlock:
                model.init_emissions_random()
                print 'Re-initializing emission probabilities'

            log_likelihood = model.expectation_maximization(corpus, args.convergence)
            if log_likelihood > best_log_likelihood:
                best_log_likelihood = log_likelihood
                best_transitions = model.transitions
                best_emissions = model.emissions

        #write the winning models
        print 'The best log likelihood was', best_log_likelihood
        outputfile = args.paramfile+'.trained'
        write_arcs(best_transitions, outputfile+'.trans')
        write_arcs(best_emissions, outputfile+'.emit')

    elif args.function == 'g':
        # write randomly generated sentences
        with codecs.open(args.corpusfile, 'w', 'utf8') as o:
            for _ in range(20):
                o.write(' '.join(model.generate(10))+'\n')  # sentences with 10 words

    print "DONE"

if __name__=='__main__':
    main()
