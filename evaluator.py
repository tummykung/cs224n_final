from optparse import OptionParser
import simplejson
import sys

resultsFile = ""
results = []
filteredSentences = {}
scores = {}

def load_results(filepath):
    with open(filepath, 'r') as f:
        lines = simplejson.loads(f.read())
        for result in lines:
            results.append(result)
    return results

def filter_results():
    for entry in results:
        if entry['type'] == 'manual_label':
            if entry['rating'] >= 1:
                val = 1
            elif entry['rating'] == 0:
                val = 0
            else:
                val = -1
            if val not in scores:
                scores[val] = []
            scores[val].append((entry['concept_polarity'],
                entry['adj_polarity'], entry['dep_polarity']))

def compute_average():
    for rating in sorted(scores.keys()):
        total = reduce(lambda x, y : (x[0] + y[0], x[1] + y[1], x[2] + y[2]), scores[rating], (0, 0, 0))
        mean = map(lambda x : x / len(scores[rating]), total)
        totalSquared = reduce(lambda x, y : (x[0] + y[0] * y[0], x[1] + y[1] * y[1],
            x[2] + y[2] * y[2]), scores[rating], (0, 0, 0))
        meanXSquared = map(lambda x : x / len(scores[rating]), totalSquared)
        xMeanSquared = map(lambda x : x * x, mean)
        variance = map(lambda x, y : x - y, meanXSquared, xMeanSquared)
        stats = zip(mean, variance)

        print rating, stats


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

