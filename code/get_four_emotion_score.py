from sentence import Sentence
import simplejson
from senticnet.senticnet import Senticnet

inputs = []
OUTPUT_FILE_PATH = "../static/test_data/sample_data.json"
sn = Senticnet()
outputs = []

def read_input():
    with open(OUTPUT_FILE_PATH, 'r') as f:
        things = simplejson.loads(f.readline())
        total = len(things)

        big_count = 0
        for each_sentence in things:
            print str(big_count) + "/" + str(total)
            big_count += 1
            tokens = Sentence(each_sentence["sentence"], 0, 0, "S").getTokens()

            pleasantness = 0.0
            aptitude = 0.0
            attention = 0.0
            sensitivity = 0.0
            count = 0
            
            for word in tokens:
                try:
                    score = sn.sentics(word)
                    pleasantness += score["pleasantness"]
                    aptitude += score["aptitude"]
                    attention += score["attention"]
                    sensitivity += score["sensitivity"]
                    count += 1
                except:
                    continue

            if count > 0:
                pleasantness = pleasantness/count
                aptitude = aptitude/count
                attention = attention/count
                sensitivity = sensitivity/count

            each_sentence["pleasantness"] = pleasantness
            each_sentence["aptitude"] = aptitude
            each_sentence["attention"] = attention
            each_sentence["sensitivity"] = sensitivity

            outputs.append(each_sentence)

def write():
    with open(OUTPUT_FILE_PATH, 'w') as f:
        f.write(simplejson.dumps(outputs))

def main():
    read_input()
    write()

if __name__ == '__main__':
    main()
