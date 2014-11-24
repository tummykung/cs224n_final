# -*- coding: utf-8 -*-
import simplejson
import nltk
from senticnet.senticnet import Senticnet
import subprocess
import ipdb
import numpy as np
import matplotlib.pyplot as plt

# ==== CONFIGURATION ====
CONCEPT_PARSER_PATH = "/Users/sorathan/Downloads/concept-parser"
LIB_PATH = CONCEPT_PARSER_PATH + "/" + "concept_parser.jar" + ":" + CONCEPT_PARSER_PATH + "/lib/*"
CONCEPT_PARSER_COMMAND_LIST = ["java", "-cp", LIB_PATH, "semantic_parser.concept_parser"]
INPUT_FILENAME = "yelp_academic_dataset_review.json"
CONCEPT_FILENAME = "concept_list.txt"
POLARITY_FILENAME = "polarity.txt"
PAIRS_FILENAME = "pairs.txt"
NUM_SAMPPLE = 600
NUM_TARGET_SENTENCES = 100
TARGET_WORD = "burger".lower()

# initialization
filtered_sentences = {}
inputs = []
sentences = {}
global_concept_list = []
cached_polarity = {}
pairs = []
sn = Senticnet() # you can do sn.concept(word), sn.polarity(word), sn.semantics(word), sn.sentics(word)
# examples
# ========
# In [12]: sn.concept("love")
# Out[12]: 
# {'polarity': 0.667,
#  'semantics': [u'sexuality',
#       u'lust',
#       u'love_another_person',
#       u'show_empathy',
#       u'beloved'],
#  'sentics': {'aptitude': 1.0,
#   'attention': 0.0,
#   'pleasantness': 1.0,
#   'sensitivity': 0.0}}


def load_pairs():
    with open(PAIRS_FILENAME, 'r') as f:
        pair_list = simplejson.loads(f.read())
        for pair in pair_list:
            pairs.append(pair)

def read_input():
    with open(INPUT_FILENAME, 'r') as f:
        for i in range(NUM_SAMPPLE):
            inputs.append(simplejson.loads(f.readline()))

    with open(CONCEPT_FILENAME, 'r') as f:
        for line in f:
            global_concept_list.append(line.strip().lower())

    with open(POLARITY_FILENAME, 'r') as f:
        dictionary = simplejson.loads(f.read())
        for key in dictionary:
            cached_polarity[key] = dictionary[key]


def filter_sentences():
    # parse sentences and also make a filter of words of interest
    for i in range(NUM_SAMPPLE):
        sentences[i] = map(lambda x: x.strip().lower(), inputs[i]['text'].split("."))
        for j in range(len(sentences[i])):
            if TARGET_WORD in sentences[i][j]:
                filtered_sentences[i] = {
                    'review_id': inputs[i]['review_id'],
                    'stars': inputs[i]['stars'],
                    'date': inputs[i]['date'],
                    'business_id': inputs[i]['business_id'],
                }
                filtered_sentences[i][j] = {'sentence': sentences[i][j]}


def compute_polarity_scores():
    num_sentence = len(filtered_sentences.keys())
    counter = 0
    for sentence_key in filtered_sentences.keys():
        counter += 1
        print ""
        print "sentence#: " + str(counter) + "/" + str(num_sentence)
        sentence_dict = filtered_sentences[sentence_key]
        num_subsentence = len(filtered_sentences[sentence_key])

        for subsentence_key in sentence_dict.keys():
            if not isinstance(subsentence_key, int):
                continue
            sentence = sentence_dict[subsentence_key]['sentence']
            # use commandline
            proc = subprocess.Popen(
                CONCEPT_PARSER_COMMAND_LIST,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout_value, stderr_value = proc.communicate(input=sentence.encode('ascii', 'ignore'))

            output_list = stdout_value.split("\n")
            print repr(output_list[0])
            concept_list = output_list[1:] # the first one is the input
            filtered_concept_list = []
            print "concept_list:"
            average_polarity = 0.0
            total_count = 0
            for concept in concept_list:
                if TARGET_WORD in concept:
                    filtered_concept_list.append(concept)
                    print "\t" + concept

                    # take an average of concept scores from the corpus
                    polarity = 0.0
                    subconcepts = concept.split("_")
                    for subconcept in subconcepts:
                        polarity += compute_polarity(subconcept)

                    # take the average
                    polarity = polarity/len(subconcepts)
                    print "\t\tpolarity: " + str(polarity)

                    total_count += 1
                    average_polarity += polarity

            # print '\tstderr:', repr(stderr_value)
            sentence_dict[subsentence_key]['full_concept'] = concept_list

            sentence_dict[subsentence_key]['filtered_concept'] = filtered_concept_list

            if total_count > 0:
                average_polarity = average_polarity/total_count
            sentence_dict[subsentence_key]['polarity'] = average_polarity
            # print "average_polarity: " + str(average_polarity)
            # print

            # get a POS tree
            tokens = nltk.word_tokenize(sentence)
            tagged = nltk.pos_tag(tokens)
            print "POS: " + repr(tagged)
            sentence_dict[subsentence_key]["tokens"] = tokens
            sentence_dict[subsentence_key]["POS"] = tagged

            adj_polarity = 0.0
            adj_count = 0
            print "adj_polarity"
            for word, POS in tagged:
                if POS in ("JJ", "JJS"):
                    adj_count += 1
                    adj_polarity += compute_polarity(word)
                    print "\t\t" + word + ": " + str(adj_polarity)
            if adj_count > 0:
                adj_polarity = adj_polarity/adj_count
            sentence_dict[subsentence_key]['adj_polarity'] = adj_polarity
            # print "average_adj_polarity: " + str(adj_polarity)

            pairs.append({
                "stars": sentence_dict['stars'],
                "polarity": average_polarity,
                "adj_polarity": adj_polarity,
                # "metadata": sentence_dict
            })

            print "stars: " + str(sentence_dict['stars'])
            print "polarity: " + str(average_polarity)
            print "adj_polarity: " + str(adj_polarity)



def compute_polarity(subconcept):
    """look up from a table if cached. Else just compute by taking average of
    the polarity scores of all the corpus concepts that contain this subconcept."""
    if subconcept in cached_polarity:
        return cached_polarity[subconcept]

    # if len(subconcept) <= 2:
        # then it's probably a preposition
        # return 0
        # NOTE: instead of doing this, we manually added prepositions to hte polarity dictionary

    count = 0
    polarity = 0.0
    for corpus_concept in global_concept_list:
        if subconcept in corpus_concept:
            count += 1
            polarity += sn.polarity(corpus_concept)
    if (count > 0):
        # take the average
        polarity = polarity/count

    # save in the cache
    cached_polarity[subconcept] = polarity
    return polarity

def save_polarity():
    with open(POLARITY_FILENAME, 'w') as f:
        f.write(simplejson.dumps(cached_polarity))

def save_pairs():
    with open(PAIRS_FILENAME, 'w') as f:
        f.write(simplejson.dumps(pairs))

def plot():
    x = map(lambda x:x["polarity"], pairs)
    y = map(lambda x:x["stars"], pairs)
    z = map(lambda x:x["adj_polarity"], pairs)
    fig, axScatter = plt.subplots(figsize=(5.5,5.5))
    axScatter.scatter(x, y)
    plt.title("polarity v.s. stars")
    plt.draw()
    plt.show()

    fig, axScatter = plt.subplots(figsize=(5.5,5.5))
    axScatter.scatter(z, y)
    plt.title("adj_polarity v.s. stars")
    plt.draw()
    plt.show()


def main():
    # load_pairs()
    read_input()
    filter_sentences()
    compute_polarity_scores()
    save_polarity()
    save_pairs()
    plot()
    ipdb.set_trace()

if __name__ == '__main__':
    main()