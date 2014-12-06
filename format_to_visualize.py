import simplejson

filtered_sentences = {}
inputs = []
businesses = []
INPUT_FILENAME = "yelp_academic_dataset_review.json"
BUSINESS_FILENAME = "yelp_academic_dataset_business.json"
# TARGET_FILENAME = "here.json"
TARGET_FILENAME = "static/test_data/sample_data.json"
NUM_SAMPLE = 10000

def original_read_input():
    with open(INPUT_FILENAME, 'r') as f:
        for i in range(NUM_SAMPLE):
            inputs.append(simplejson.loads(f.readline()))

    with open(BUSINESS_FILENAME, 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            businesses.append(simplejson.loads(line))

def read_input():
    with open("burger.json", 'r') as f:
        while True:
            line = f.readline()
            if not line:
                break
            currEntry = simplejson.loads(line)
            currKey = currEntry["sentence_key"]
            currSubKey = currEntry["subsentence_key"]
            if not currKey in filtered_sentences:
                filtered_sentences[currKey] = {}
            # filtered_sentences[currKey][currSubKey] = currEntry
            filtered_sentences[currKey][currSubKey] = {}
            filtered_sentences[currKey][currSubKey]["rating"] = currEntry["rating"]
            filtered_sentences[currKey][currSubKey]["sentence"] = currEntry["sentence"]
            # filtered_sentences[currKey][currSubKey]["review_id"] = inputs[currKey]["review_id"]
            filtered_sentences[currKey][currSubKey]["business_id"] = inputs[currKey]["business_id"]
            biz_id = inputs[currKey]["business_id"]
            filtered_sentences[currKey][currSubKey]["user_id"] = inputs[currKey]["user_id"]

            filtered_sentences[currKey][currSubKey]["votes"] = inputs[currKey]["votes"]
            filtered_sentences[currKey][currSubKey]["stars"] = inputs[currKey]["stars"]
            business = filter(lambda x:x["business_id"] == biz_id, businesses)[0]
            filtered_sentences[currKey][currSubKey]["lng"] = business["longitude"]
            filtered_sentences[currKey][currSubKey]["full_address"] = business["full_address"]
            filtered_sentences[currKey][currSubKey]["lat"] = business["latitude"]
            filtered_sentences[currKey][currSubKey]["name"] = business["name"]

def write():
    to_write = []
    for currKey in filtered_sentences:
        for subsentence_key in filtered_sentences[currKey]:
            to_write.append(filtered_sentences[currKey][subsentence_key])

    with open(TARGET_FILENAME, 'w') as f:
        f.write(simplejson.dumps(to_write))

def main():
    original_read_input()
    read_input()
    write()

if __name__ == '__main__':
    main()