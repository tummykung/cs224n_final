import os
import nltk
import simplejson
import ipdb
from sentence import Sentence
from senticnet.senticnet import Senticnet
from httplib import BadStatusLine

# ==== CONFIGURATION ====
CACHE_DIR = "caches/"
DATA_DIR = "data/"
CONCEPT_FILENAME = DATA_DIR + "concept_list.txt"
POLARITY_FILENAME = CACHE_DIR + "polarity.txt"
VERBOSE = True

# initialization
cached_polarity = {}
global_concept_list = []
sn = Senticnet() # you can call sn.concept(word), sn.polarity(word), sn.semantics(word), sn.sentics(word)

def cache_polarity():
    with open(POLARITY_FILENAME, 'w') as f:
        f.write(simplejson.dumps(cached_polarity))

def load_cached_polarity():
    print "Loading polarity cache"
    with open(POLARITY_FILENAME, 'r') as f:
        dictionary = simplejson.loads(f.read())
        for key in dictionary:
            cached_polarity[key] = dictionary[key]

def load_concept_list():
    with open(CONCEPT_FILENAME, 'r') as f:
        for line in f:
            global_concept_list.append(line.strip().lower())

def compute_concept_polarity(foodName, sentence):
    concept_list = sentence.getConcepts()
    filtered_concept_list = []
    if VERBOSE:
        print "concept_list:"
    concept_polarity = 0.0
    total_count = 0
    for concept in concept_list:
        if foodName in concept:
            filtered_concept_list.append(concept)
            if VERBOSE:
                print "\t" + concept

            # take an average of concept scores from the corpus
            polarity = 0.0
            subconcepts = concept.split("_")
            for subconcept in subconcepts:
                polarity += _compute_polarity(subconcept)

            # take the average
            polarity = polarity/len(subconcepts)
            if VERBOSE:
                print "\t\tpolarity: " + str(polarity)

            total_count += 1
            concept_polarity += polarity
    if total_count > 0:
        concept_polarity = concept_polarity/total_count
    return concept_polarity, filtered_concept_list


def compute_adj_polarity(foodName, sentence):
    tagged = sentence.getPOS()
    adj_polarity = 0.0
    adj_count = 0
    if VERBOSE:
        print "POS: " + repr(sentence.getPOS())
    if VERBOSE:
        print "adj_polarity"
    for word, POS in tagged:
        if POS in ("JJ", "JJS"):
            adj_count += 1
            adj_polarity += _compute_polarity(word)
            if VERBOSE:
                print "\t\t" + word + ": " + str(adj_polarity)
    if adj_count > 0:
        adj_polarity = adj_polarity/adj_count
    return adj_polarity


def compute_dep_polarity(foodName, sentence):

    tagged = sentence.getPOS()
    graph = sentence.getGraph()
    dep_polarity = 0.0
    dep_count = 0
    if VERBOSE:
        print "dep_polarity"
    if VERBOSE:
        print graph.tree().pprint()
    for i,node in enumerate(graph.nodelist):
        if node['word'] and foodName in node['word']:
            for deps in graph.get_by_address(i)['deps']:
                currWord = tagged[deps - 1][0]
                currTag = tagged[deps - 1][1]
                if VERBOSE:
                    print "evaluating: ", currWord, currTag
                if currTag in ("JJ", "JJS", "JJR"):
                    currPolarity = _compute_polarity(currWord)
                    if currPolarity != 0:
                        dep_polarity += currPolarity
                        dep_count += 1
                        if VERBOSE:
                            print "dependency: ", currWord, currTag, currPolarity
            inverted = 1;
            path = graph.get_cycle_path(graph.root, i)
            path.reverse()
            for parents in path:
                currWord = tagged[parents - 1][0]
                currTag = tagged[parents - 1][1]
                if VERBOSE:
                    print "evaluating: ", currWord, currTag
                currPolarity = inverted * _compute_polarity(currWord)
                if currTag in ("VB", "VBN", "VBD", "VBZ", "VBP", "VBG"):
                    currDeps = map(lambda x : tagged[x - 1][0],
                            graph.get_by_address(parents)['deps'])
                    if len(filter(lambda x : x in ("except", "but", "not", "dont",
                        "than", "no", "never"), currDeps)) > 0:
                        currPolarity *= -1
                        print "NEGATING"
                if currPolarity != 0:
                    dep_polarity += currPolarity
                    dep_count += 1
                    if VERBOSE:
                        print "parent: ", currWord, currTag, currPolarity
    if dep_count > 0:
        dep_polarity = dep_polarity / dep_count
    return dep_polarity


def _compute_polarity_from_cache(subconcept):
    subconcept = stem(subconcept)

    if not global_concept_list:
        load_concept_list()
    
    if subconcept in cached_polarity:
        return cached_polarity[subconcept]
    return None


def _compute_polarity(subconcept):
    subconcept = stem(subconcept)

    if not global_concept_list:
        load_concept_list()
    
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
        if subconcept == corpus_concept:
            count = 1
            gotIt = False
            while not gotIt: 
                try:
                    polarity = sn.polarity(corpus_concept)
                    gotIt = True
                except BadStatusLine:
                    print "Time out on polarity fetch for ", corpus_concept, " retrying..."
            break
        if subconcept in corpus_concept.split("_"):
            count += 1
            gotIt = False
            while not gotIt: 
                try:
                    polarity += sn.polarity(corpus_concept)
                    gotIt = True
                except BadStatusLine:
                    print "Time out on polarity fetch for ", corpus_concept, " retrying..."
    if (count > 0):
        # take the average
        polarity = polarity/count

    # save in the cache
    cached_polarity[subconcept] = polarity
    return polarity

def stem(word):
    for suffix in ['ing', 'ly', 'ed', 'ious', 'ies', 'ive', 'es', 's', 'ment']:
        if word.endswith(suffix):
            return word[:-len(suffix)]
    return word


