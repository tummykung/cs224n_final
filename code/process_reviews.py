# -*- coding: utf-8 -*-
import simplejson
import ipdb
import os
from sentence import Sentence
import polarity
import sys
import matplotlib.pyplot as plt
from optparse import OptionParser

# ==== CONFIGURATION ====
DATA_DIR = "../data/"
INPUT_FILENAME = DATA_DIR + "yelp_academic_dataset_review.json"
BUSINESS_FILENAME = DATA_DIR + "yelp_academic_dataset_business.json"
NUM_SAMPLE = 50000
OUTPUT_FILE_PATH = ""

# initialization
beginTrain = -1
endTrain = -1
filtered_sentences = {}
results = []
inputs = []
businesses = []
sentences = {}
human = False
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


def load_results(filepath):
    with open(filepath, 'r') as f:
        lines = simplejson.loads(f.read())
        for result in lines:
            results.append(result)
    return results

def read_input():
    with open(INPUT_FILENAME, 'r') as f:
        for i in range(NUM_SAMPLE):
            inputs.append(simplejson.loads(f.readline()))
    with open(BUSINESS_FILENAME, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            businesses.append(simplejson.loads(line))

def filter_sentences():
    if os.path.isfile(foodName + ".json"):
        read_human_labeled()
    else:
        read_raw()

# parse sentences and also make a filter of words of interest
def read_raw():
    print "Reading directly from raw yelp data"
    global human
    human = False
    i = 0
    hitCounter = 0
    while hitCounter < endTrain:
        sentences[i] = map(lambda x: x.strip().lower(), inputs[i]['text'].split("."))
        for j in range(len(sentences[i])):
            if foodName in sentences[i][j]:
                if i not in filtered_sentences:
                    hitCounter += 1
                    filtered_sentences[i] = {
                        'review_id': inputs[i]['review_id'],
                        'stars': inputs[i]['stars'],
                        'date': inputs[i]['date'],
                        'business_id': inputs[i]['business_id'],
                    }
                filtered_sentences[i][j] = {'sentence': sentences[i][j]}
        i += 1


def read_human_labeled():
    print "Reading from human-labeled data"
    global human
    human = True
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


def compute_polarity_scores():
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
            sentence = Sentence(sentence_dict[subsentence_key]['sentence'], sentence_key, subsentence_key, foodName)
            concept_polarity, filtered_concept_list = polarity.compute_concept_polarity(foodName, sentence)
            adj_polarity = polarity.compute_adj_polarity(foodName, sentence)
            dep_polarity = polarity.compute_dep_polarity(foodName, sentence)

            business = filter(lambda x:x["business_id"] == inputs[sentence_key]["business_id"], businesses)[0]
            results.append({
                "rating": sentence_dict[subsentence_key]['rating'] if human else dep_polarity,
                "type": "manual_label" if human else "dep_polarity",
                "concept_polarity": concept_polarity,
                "adj_polarity": adj_polarity,
                "dep_polarity": dep_polarity,
                "id": i,
                "sentence": sentence.str_val,
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
                "concepts": sentence.getConcepts(),
                "filtered_concepts": filtered_concept_list
            })

            if human:
                print "rating: " + str(sentence_dict[subsentence_key]['rating'])
            print "concept_polarity: " + str(concept_polarity)
            print "adj_polarity: " + str(adj_polarity)
            print "dep_polarity: " + str(dep_polarity)



def save_results():
    with open(OUTPUT_FILE_PATH, 'w') as f:
        f.write(simplejson.dumps(results))

def plot():
    x = map(lambda x:x["concept_polarity"], results)
    y = map(lambda x:x["rating"], results)
    z = map(lambda x:x["adj_polarity"], results)
    w = map(lambda x:x["dep_polarity"], results)
    fig, axScatter = plt.subplots(figsize=(5.5,5.5))
    axScatter.scatter(x, y)
    plt.title("concept_polarity v.s. rating")
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

def load_caches():
    polarity.load_cached_polarity()
    Sentence.load_cached_parses()
    Sentence.load_cached_concepts()

def save_caches():
    polarity.cache_polarity()
    Sentence.cache_parses()
    Sentence.cache_concepts()

def main(save):
    read_input()
    load_caches()
    filter_sentences()
    compute_polarity_scores()
    # poor man's concurrency guard, in case some other process wrote to cache
    load_caches()
    save_caches()
    if save:
        load_results(OUTPUT_FILE_PATH)
        save_results()
    # plot()

if __name__ == '__main__':
    print "use '--save_results ../static/test_data/sample_data.json' to append results there."
    args = sys.argv[1:]
    parser = OptionParser(usage=main.__doc__)
    parser.add_option(
        '--save_results',
        dest="save",
        default=None,
    )
    options, arguments = parser.parse_args(args)
    if len(arguments) != 3:
        print "Invalid number of arguments, need: python process_reviews.py foodName beginTrain endTrain"
        exit(0)
    try:
        foodName = arguments[0]
        beginTrain = int(arguments[1])
        endTrain = int(arguments[2])
        OUTPUT_FILE_PATH = options.save
    except ValueError:
        print "Bad input arguments!"
        exit(0)

    save = False
    if (options.save):
        save = True
    main(save)

