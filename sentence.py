import nltk
import subprocess
import os

# ==== CONFIGURATION ====
CONCEPT_PARSER_PATH = os.getenv("HOME") + "/concept-parser"
LIB_PATH = CONCEPT_PARSER_PATH + "/" + "concept_parser.jar" + ":" + CONCEPT_PARSER_PATH + "/lib/*"
CONCEPT_PARSER_COMMAND_LIST = ["java", "-cp", LIB_PATH, "semantic_parser.concept_parser"]

class Sentence:
    def __init__(self, str_val):
        self.str_val = str_val
        self._tokens = []
        self._POS = []
        self._concept_list = []

    def getPOS(self):
        if not self._POS:
            tokens = self.getTokens()
            self._POS = nltk.pos_tag(tokens)
        return self._POS

    def getTokens(self):
        if not self._tokens:
            self._tokens = nltk.word_tokenize(self.str_val)
        return self._tokens

    def getConcepts(self):
        if not self._concept_list:
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
        return self._concept_list
