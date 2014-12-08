from optparse import OptionParser
import simplejson
import sys
import math
import numpy as np

resultsFile = ""
filteredSentences = {}
scores = {}
allScores = []
results = []

def load_results(filepath):
    with open(filepath, 'r') as f:
        lines = simplejson.loads(f.read())
        for result in lines:
            results.append(result)
    return results

def filter_results():
    firstPass = filter(lambda x : x['type'] == 'manual_label', results)
    negatives = filter(lambda x : x['rating'] < 0, firstPass)
    neutrals = filter(lambda x : x['rating'] == 0, firstPass)
    positives = filter(lambda x : x['rating'] > 0, firstPass)
    allScores = np.zeros(shape=(len(firstPass),3))
    scores[-1] = np.zeros(shape=(len(negatives),3))
    scores[0] = np.zeros(shape=(len(neutrals),3))
    scores[1] = np.zeros(shape=(len(positives),3))
    counters = {-1 : 0, 0 : 0, 1: 0}
    for i,entry in enumerate(firstPass):
        allScores[i][0] = entry['concept_polarity']
        allScores[i][1] = entry['adj_polarity']
        allScores[i][2] = entry['dep_polarity']
    for entry in firstPass:
        if entry['rating'] >= 1:
            val = 1
        elif entry['rating'] == 0:
            val = 0
        else:
            val = -1
        scores[val][counters[val]][0] = (entry['concept_polarity'] -
                np.mean(allScores[:,0])) / np.std(allScores[:,0])
        scores[val][counters[val]][1] = (entry['adj_polarity'] -
                np.mean(allScores[:,1])) / np.std(allScores[:,1])
        scores[val][counters[val]][2] = (entry['dep_polarity'] -
                np.mean(allScores[:,2])) / np.std(allScores[:,2])
        counters[val] += 1

def compute_average():
    means = np.zeros(shape=(3,3))
    stdDevs = np.zeros(shape=(3,3))
    for j,rating in enumerate(sorted(scores.keys())):
        print j,
        for i in range(0,3):
            curr = scores[rating][:,i]
            means[j][i] = np.mean(curr)
            stdDevs[j][i] = np.std(curr)
            print str.format('{0:.3f}', means[j][i]), str.format('{0:.3f}',stdDevs[j][i]), 
        print



def main():
    load_results(resultsFile)
    filter_results()
    compute_average()

if __name__ == '__main__':
    args = sys.argv[1:]
    parser = OptionParser(usage=main.__doc__)
    options, arguments = parser.parse_args(args)
    if len(arguments) != 1:
        print "Invalid number of arguments, need: python evaluation.py results_file"
        exit(0)
    try:
        resultsFile = arguments[0]
    except ValueError:
        print "Bad input arguments!"
        exit(0)

    main()

