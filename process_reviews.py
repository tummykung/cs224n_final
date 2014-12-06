# -*- coding: utf-8 -*-
import simplejson
import nltk
from nltk.stem import WordNetLemmatizer
from senticnet.senticnet import Senticnet
import subprocess
import ipdb
import numpy as np
import os
import sys
import matplotlib.pyplot as plt

# ==== CONFIGURATION ====
CONCEPT_PARSER_PATH = os.getenv("HOME") + "/concept-parser"
MALT_PARSER_PATH = os.getenv("HOME") + "/maltparser-1.8.1"
LIB_PATH = CONCEPT_PARSER_PATH + "/" + "concept_parser.jar" + ":" + CONCEPT_PARSER_PATH + "/lib/*"
CONCEPT_PARSER_COMMAND_LIST = ["java", "-cp", LIB_PATH, "semantic_parser.concept_parser"]
CONCEPT_FILENAME = "concept_list.txt"
POLARITY_FILENAME = "polarity.txt"
INPUT_FILENAME = "yelp_academic_dataset_review.json"
BUSINESS_FILENAME = "yelp_academic_dataset_business.json"
NUM_TARGET_SENTENCES = 100
NUM_SAMPLE = 10000
OUTPUT_FILE_PATH = ""

# initialization
beginTrain = -1
cached_polarity = {}
endTrain = -1
filtered_sentences = {}
global_concept_list = []
results = []
sn = Senticnet() # you can call sn.concept(word), sn.polarity(word), sn.semantics(word), sn.sentics(word)
inputs = []
businesses = []
sentences = {}
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


def load_results():
    with open(OUTPUT_FILE_PATH, 'r') as f:
        results = simplejson.loads(f.read())
        for result in results:
            results.append(pair)

def original_read_input():
    with open(INPUT_FILENAME, 'r') as f:
        for i in range(NUM_SAMPLE):
            inputs.append(simplejson.loads(f.readline()))
    with open(CONCEPT_FILENAME, 'r') as f:
        for line in f:
            global_concept_list.append(line.strip().lower())

    with open(POLARITY_FILENAME, 'r') as f:
        dictionary = simplejson.loads(f.read())
        for key in dictionary:
            cached_polarity[key] = dictionary[key]

    with open(BUSINESS_FILENAME, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            businesses.append(simplejson.loads(line))

def filter_sentences():
    # parse sentences and also make a filter of words of interest
    for i in range(NUM_SAMPLE):
        sentences[i] = map(lambda x: x.strip().lower(), inputs[i]['text'].split("."))
        for j in range(len(sentences[i])):
            if foodName in sentences[i][j]:
                if i not in filtered_sentences:
                    filtered_sentences[i] = {
                        'review_id': inputs[i]['review_id'],
                        'stars': inputs[i]['stars'],
                        'date': inputs[i]['date'],
                        'business_id': inputs[i]['business_id'],
                    }
                filtered_sentences[i][j] = {'sentence': sentences[i][j]}

def read_input():
    with open(foodName + ".json", 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            currEntry = simplejson.loads(line)
            currKey = currEntry["sentence_key"]
            currSubKey = currEntry["subsentence_key"]
            if not currKey in filtered_sentences:
                filtered_sentences[currKey] = {}
            filtered_sentences[currKey][currSubKey] = currEntry
    with open(CONCEPT_FILENAME, 'r') as f:
        for line in f:
            global_concept_list.append(line.strip().lower())

    with open(POLARITY_FILENAME, 'r') as f:
        dictionary = simplejson.loads(f.read())
        for key in dictionary:
            cached_polarity[key] = dictionary[key]

def compute_polarity_scores():
    num_sentence = len(filtered_sentences.keys())
    for i, sentence_key in enumerate(sorted(filtered_sentences)):
        if i < beginTrain or i > endTrain:
            continue
        print
        print "==============================="
        print "sentence#: " + str(i) + " -- " + str(i - beginTrain + 1) +  "/" + str(endTrain - beginTrain + 1)
        print
        sentence_dict = filtered_sentences[sentence_key]
        subsentence_keys = sorted(filter(lambda x: isinstance(x, int), sentence_dict.keys()))

        for j, subsentence_key in enumerate(subsentence_keys):
            print
            print "-------------------------------"
            print "subsentence#: " + str(j + 1) + "/" + str(len(subsentence_keys))
            print
            sentence = sentence_dict[subsentence_key]['sentence']
            #print sentence
            #continue
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
                if foodName in concept:
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

            dep_polarity = 0.0
            dep_count = 0
            print "dep_polarity"
            parser = nltk.parse.malt.MaltParser(working_dir=MALT_PARSER_PATH,mco="engmalt.linear-1.7")
            graph = parser.tagged_parse(tagged)
            #print graph.tree().pprint()
            for i,node in enumerate(graph.nodelist):
                if node['word'] and foodName in node['word']:
                    for deps in graph.get_by_address(i)['deps']:
                        currWord = tagged[deps - 1][0]
                        currTag = tagged[deps - 1][1]
                #        print "evaluating: ", currWord, currTag
                        if currTag in ("JJ", "JJS", "JJR", "NN", "NNS", "NNP"):
                            currPolarity = compute_polarity(currWord)
                            if currPolarity != 0:
                                dep_polarity += currPolarity
                                dep_count += 1
                                print "dependency: ", currWord, currTag, currPolarity
                    inverted = 1;
                    path = graph.get_cycle_path(graph.root, i)
                    path.reverse()
                    for parents in path:
                        currWord = tagged[parents - 1][0]
                        currTag = tagged[parents - 1][1]
                #        print "evaluating: ", currWord, currTag
                        if currWord in ("except", "not", "dont", "than", "no", "never"):
                            inverted = -1 * inverted
                            continue
                        if currTag in ("VBN", "VBD", "VBZ", "VBP", "JJR", "JJ", "JJS"):
                            currPolarity = inverted * compute_polarity(currWord)
                            if currPolarity != 0:
                                dep_polarity += currPolarity
                                dep_count += 1
                                #print "parent: ", currWord, currTag, currPolarity
            if dep_count > 0:
                dep_polarity = dep_polarity / dep_count

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

            business = filter(lambda x:x["business_id"] == inputs[sentence_key]["business_id"], businesses)[0]
            results.append({
                "rating": dep_polarity, # for now, we'll use the dep_polarity as the main rating
                "type": "dep_polarity",
                "polarity": average_polarity,
                "adj_polarity": adj_polarity,
                "dep_polarity": dep_polarity,
                "id": i,
                "sentence": sentence,
                "sentence_key": sentence_key,
                "subsentence_key": subsentence_key,
                "business_id": inputs[sentence_key]["business_id"],
                "user_id": inputs[sentence_key]["user_id"],
                "votes": inputs[sentence_key]["votes"],
                "stars": inputs[sentence_key]["stars"],
                "lng": business["longitude"],
                "lat": business["latitude"],
                "full_address": business["full_address"],
                "name": business["name"],
                "food": foodName,
                "concepts": sentence_dict[subsentence_key]['full_concept'],
                "filtered_concepts": sentence_dict[subsentence_key]['filtered_concept']
            })

            # print "rating: " + str(sentence_dict[subsentence_key]['rating'])
            print "polarity: " + str(average_polarity)
            print "adj_polarity: " + str(adj_polarity)
            print "dep_polarity: " + str(dep_polarity)

def stem(word):
    for suffix in ['ing', 'ly', 'ed', 'ious', 'ies', 'ive', 'es', 's', 'ment']:
        if word.endswith(suffix):
            return word[:-len(suffix)]
    return word


def compute_polarity(subconcept):
    subconcept = stem(subconcept)
    
    """look up from a table if cached. Else just compute by taking the average of
    the polarity scores of all the corpus concepts that contain this subconcept."""
    if subconcept in cached_polarity:
        return cached_polarity[subconcept]


    # if len(subconcept) <= 2:
        # then it's probably a preposition
        # return 0
        # NOTE: instead of doing this, we manually added prepositions to the polarity dictionary

    count = 0
    polarity = 0.0
    for corpus_concept in global_concept_list:
        if subconcept in corpus_concept.split("_"):
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

def save_results():
    with open(OUTPUT_FILE_PATH, 'w') as f:
        f.write(simplejson.dumps(results))

def plot():
    x = map(lambda x:x["polarity"], results)
    y = map(lambda x:x["rating"], results)
    z = map(lambda x:x["adj_polarity"], results)
    w = map(lambda x:x["dep_polarity"], results)
    fig, axScatter = plt.subplots(figsize=(5.5,5.5))
    axScatter.scatter(x, y)
    plt.title("polarity v.s. rating")
    plt.draw()
    plt.show()

    fig, axScatter = plt.subplots(figsize=(5.5,5.5))
    axScatter.scatter(z, y)
    plt.title("adj_polarity v.s. rating")
    plt.draw()
    plt.show()

    fig, axScatter = plt.subplots(figsize=(5.5,5.5))
    axScatter.scatter(w, y)
    plt.title("dep_polarity v.s. rating")
    plt.draw()
    plt.show()

def main():
    load_results()
    original_read_input()
    filter_sentences()
    # read_input()
    compute_polarity_scores()
    save_polarity()
    save_results()
    # plot()

if __name__ == '__main__':
    "see results in static/test_data/sample_data.json"
    if len(sys.argv) != 4:
        print "Invalid number of arguments, need: python process_reviews.py foodName beginTrain endTrain"
        exit(0)
    try:
        foodName = sys.argv[1]
        beginTrain = int(sys.argv[2])
        endTrain = int(sys.argv[3])
        OUTPUT_FILE_PATH = "static/test_data/sample_data.json"
    except ValueError:
        print "Bad input arguments!"
        exit(0)

    main()

