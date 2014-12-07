import ipdb
import nltk
import subprocess
import os
import simplejson

# ==== CONFIGURATION ====
CONCEPT_PARSER_PATH = os.getenv("HOME") + "/concept-parser"
LIB_PATH = CONCEPT_PARSER_PATH + "/" + "concept_parser.jar" + ":" + CONCEPT_PARSER_PATH + "/lib/*"
CONCEPT_PARSER_COMMAND_LIST = ["java", "-cp", LIB_PATH, "semantic_parser.concept_parser"]
CONCEPT_CACHE_FILENAME = "concept_cache.txt"
MALT_PARSER_PATH = os.getenv("HOME") + "/maltparser-1.8.1"
PARSES_FILENAME = "parses.txt"
parser = nltk.parse.malt.MaltParser(working_dir=MALT_PARSER_PATH,mco="engmalt.linear-1.7")

# initialization

class Sentence:
    _cached_concepts = {}
    _cached_parses = {}

    def __init__(self, str_val, key, subkey):
        self.str_val = str_val
        self.key = str(key)
        self.subkey = str(subkey)
        self._tokens = []
        self._POS = []
        self._concept_list = []
        self._graph = []

    def getPOS(self):
        if not self._POS:
            tokens = self.getTokens()
            self._POS = nltk.pos_tag(tokens)
        return self._POS

    def getTokens(self):
        if not self._tokens:
            self._tokens = nltk.word_tokenize(self.str_val)
        return self._tokens

    def getGraph(self):
        if self._graph:
            #already loaded
            return self._graph
        elif self.key in Sentence._cached_parses and self.subkey in Sentence._cached_parses[self.key]:
            self._graph = nltk.parse.DependencyGraph(Sentence._cached_parses[self.key][self.subkey])
        else:
            self._graph = parser.tagged_parse(self.getPOS())
            if self.key not in Sentence._cached_parses:
                Sentence._cached_parses[self.key] = {}
            Sentence._cached_parses[self.key][self.subkey] = self._graph.to_conll(4)
        return self._graph


    def getConcepts(self):
        if self._concept_list:
            # already loaded
            return self._concept_list
        elif self.key in Sentence._cached_concepts and self.subkey in Sentence._cached_concepts[self.key]:
            # in cache
            self._concept_list = Sentence._cached_concepts[self.key][self.subkey]
        else:
            # otherwise, need to generate
            # use commandline
            proc = subprocess.Popen(
                CONCEPT_PARSER_COMMAND_LIST,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout_value, stderr_value = proc.communicate(input=self.str_val.encode('ascii', 'ignore'))

            output_list = stdout_value.split("\n")
            self._concept_list = output_list[1:] # the first one is the input

            if self.key not in Sentence._cached_concepts:
                Sentence._cached_concepts[self.key] = {}
            Sentence._cached_concepts[self.key][self.subkey] = self._concept_list

        return self._concept_list

    @staticmethod
    def cache_concepts():
        with open(CONCEPT_CACHE_FILENAME, 'w') as f:
            f.write(simplejson.dumps(Sentence._cached_concepts))

    @staticmethod
    def cache_parses():
        with open(PARSES_FILENAME, 'w') as f:
            f.write(simplejson.dumps(Sentence._cached_parses))

    @staticmethod
    def load_cached_concepts():
        print "Loading concept cache"
        with open(CONCEPT_CACHE_FILENAME, 'r') as f:
            dictionary = simplejson.loads(f.read())
            for key in dictionary:
                Sentence._cached_concepts[key] = dictionary[key]

    @staticmethod
    def load_cached_parses():
        print "Loading parse cache"
        with open(PARSES_FILENAME, 'r') as f:
            dictionary = simplejson.loads(f.read())
            for key in dictionary:
                Sentence._cached_parses[key] = dictionary[key]
