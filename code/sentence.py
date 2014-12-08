# -*- coding: utf-8 -*-
import ipdb
import nltk
import subprocess
import os
import simplejson

# ==== CONFIGURATION ====
CACHE_DIR = "caches/"
CONCEPT_PARSER_PATH = os.getenv("HOME") + "/concept-parser"
LIB_PATH = CONCEPT_PARSER_PATH + "/" + "concept_parser.jar" + ":" + CONCEPT_PARSER_PATH + "/lib/*"
CONCEPT_PARSER_COMMAND_LIST = ["java", "-cp", LIB_PATH, "semantic_parser.concept_parser"]
CONCEPT_CACHE_FILENAME = CACHE_DIR + "concept_cache.txt"
MALT_PARSER_PATH = os.getenv("HOME") + "/maltparser-1.8.1"
PARSES_FILENAME = CACHE_DIR + "parses.txt"
parser = nltk.parse.malt.MaltParser(working_dir=MALT_PARSER_PATH,mco="engmalt.linear-1.7")

# initialization

class Sentence:
    _cached_concepts = {}
    _cached_parses = {}

    def __init__(self, str_val, key, subkey, food):
        self.str_val = str_val
        self.key = str(key)
        self.subkey = str(subkey)
        self._tokens = []
        self._POS = []
        self._concept_list = []
        self._graph = []
        self.food = food

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
        elif self.food in Sentence._cached_parses and self.key in Sentence._cached_parses[self.food] and self.subkey in Sentence._cached_parses[self.food][self.key]:
            self._graph = nltk.parse.DependencyGraph(Sentence._cached_parses[self.food][self.key][self.subkey])
        else:
            tagged = self.getPOS()
            # BECAUSE I CANT FIGURE OUT HOW TO GET THE MALT PARSER NLTK WRAPPER
            # TO WORK WITH THIS OMG
            if self.food == "lobster" and self.key == "21770" and self.subkey == "3":
                tagged[14] = (u'brule', 'NN')
            self._graph = parser.tagged_parse(tagged)
            if self.food not in Sentence._cached_parses:
                Sentence._cached_parses[self.food] = {}
            if self.key not in Sentence._cached_parses[self.food]:
                Sentence._cached_parses[self.food][self.key] = {}
            Sentence._cached_parses[self.food][self.key][self.subkey] = self._graph.to_conll(4)
        return self._graph


    def getConcepts(self):
        if self._concept_list:
            # already loaded
            return self._concept_list
        elif self.food in Sentence._cached_concepts and self.key in Sentence._cached_concepts[self.food] and self.subkey in Sentence._cached_concepts[self.food][self.key]:
            # in cache
            self._concept_list = Sentence._cached_concepts[self.food][self.key][self.subkey]
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

            if self.food not in Sentence._cached_concepts:
                Sentence._cached_concepts[self.food] = {}
            if self.key not in Sentence._cached_concepts[self.food]:
                Sentence._cached_concepts[self.food][self.key] = {}
            Sentence._cached_concepts[self.food][self.key][self.subkey] = self._concept_list

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
            for food in dictionary:
                if food not in Sentence._cached_concepts:
                    Sentence._cached_concepts[food] = {}

                for key in dictionary[food]:
                    Sentence._cached_concepts[food][key] = dictionary[food][key]

    @staticmethod
    def load_cached_parses():
        print "Loading parse cache"
        with open(PARSES_FILENAME, 'r') as f:
            dictionary = simplejson.loads(f.read())
            for food in dictionary:
                if food not in Sentence._cached_parses:
                    Sentence._cached_parses[food] = {}
                for key in dictionary[food]:
                    Sentence._cached_parses[food][key] = dictionary[food][key]
