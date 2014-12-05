import simplejson
import process_reviews
import sys

outputFileName = ""
outputs = []
beginRange = -1
endRange = -1

def main():
    process_reviews.read_input()
    process_reviews.filter_sentences()
    rate()


def rate():
    num_sentence = len(process_reviews.filtered_sentences.keys())
    for i,sentence_key in enumerate(sorted(process_reviews.filtered_sentences.keys())):
        if i < beginRange or i > endRange:
            continue
        print "==============================="
        print "sentence#: " + str(i + 1) + "/" + str(num_sentence)
        print ""
        sentence_dict = process_reviews.filtered_sentences[sentence_key]
        for subsentence_key in sorted(filter(lambda x: isinstance(x, int), sentence_dict.keys())):
            sentence = sentence_dict[subsentence_key]['sentence']
            print "-------------------------------"
            print "subsentence#: " + str(subsentence_key)
            print ""
            print sentence
            print ""
            valid = False
            while not valid:
                rating = raw_input("Rate this sentence: ")
                print ""
                try:
                    rating = int(rating)
                except ValueError:
                    print "Bad input, try again."
                    continue
                if rating < -2 or rating > 2:
                    print "Out of range, try again."
                    continue
                
                valid = True
                output = {
                    "id": i,
                    "sentence": sentence,
                    "sentence_key": sentence_key,
                    "subsentence_key": subsentence_key,
                    "rating": rating,
                }
                with open(outputFileName, 'a') as f:
                    f.write(simplejson.dumps(output))
                    f.write('\n')

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print "Invalid number of arguments, need: python ranker.py beginRange endRange outputFileName"
        exit(0)
    try:
        beginRange = int(sys.argv[1])
        endRange = int(sys.argv[2])
        outputFileName = sys.argv[3]
    except ValueError:
        print "Bad input arguments, begin and end range need to be integers!"
        exit(0)
    main()
