import simplejson
import sys

# ==== CONFIGURATION ====
INPUT_FILENAME = "yelp_academic_dataset_review.json"

# initialization
foodName = ""
beginRange = -1
endRange = -1
filtered_sentences = {}
outputs = []

def main():
    filter_sentences()
    rate()

def filter_sentences():
    counter = 0
    overallIndex = 0
    with open(INPUT_FILENAME, 'r') as f:
        while True:
            inputLine = simplejson.loads(f.readline())
            # parse sentences and also make a filter of words of interest
            sentences = map(lambda x: x.strip().lower(), inputLine['text'].split("."))
            for j in range(len(sentences)):
                if foodName in sentences[j]:
                    if overallIndex not in filtered_sentences:
                        # Only want to count the overall review once.
                        counter += 1
                        if counter - 1 < beginRange:
                            break
                        filtered_sentences[overallIndex] = {
                            'review_id': inputLine['review_id'],
                            'stars': inputLine['stars'],
                            'date': inputLine['date'],
                            'business_id': inputLine['business_id'],
                        }
                    filtered_sentences[overallIndex][j] = {'sentence': sentences[j]}
            if counter > endRange:
                break
            overallIndex += 1




def rate():
    num_sentence = len(filtered_sentences.keys())
    for i,sentence_key in enumerate(sorted(filtered_sentences.keys())):
        print "==============================="
        print "sentence#: " + str(i + 1) + "/" + str(num_sentence)
        print ""
        sentence_dict = filtered_sentences[sentence_key]
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
                with open(foodName + ".json", 'a') as f:
                    f.write(simplejson.dumps(output))
                    f.write('\n')

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print "Invalid number of arguments, need: python ranker.py beginRange endRange foodName"
        exit(0)
    try:
        beginRange = int(sys.argv[1])
        endRange = int(sys.argv[2])
        foodName = sys.argv[3]
    except ValueError:
        print "Bad input arguments, begin and end range need to be integers!"
        exit(0)
    main()
