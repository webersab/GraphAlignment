#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
This file is adapted from a file of the same name which is part of
UDPipe <http://github.com/ufal/udpipe/>.

Copyright 2016 Institute of Formal and Applied Linguistics, Faculty of
Mathematics and Physics, Charles University in Prague, Czech Republic.

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

# Standard
from ufal.udpipe import Model, InputFormat, OutputFormat, ProcessingError, Sentence


class UDPipeModel:

    """
    Perform UDPipe preprocessing, as required by the UnstableParser
    """
    
    def __init__(self, path):
        """Load given model."""
        self.model = Model.load(path)
        if not self.model:
            raise Exception("Cannot load UDPipe model from file '%s'" % path)

        
    def tokenize(self, text):
        """Tokenize the text and return list of ufal.udpipe.Sentence-s."""
        tokenizer = self.model.newTokenizer("normalized_spaces;presegmented")
        if not tokenizer:
            raise Exception("The model does not have a tokenizer")
        return self._read(text, tokenizer)


    def _read(self, text, input_format):
        """Read sentences"""
        input_format.setText(text)
        error = ProcessingError()
        sentences = []
        sentence = Sentence()
        while input_format.nextSentence(sentence, error):
            sentences.append(sentence)
            sentence = Sentence()
        if error.occurred():
            raise Exception(error.message)
        return sentences

    
    def tag(self, sentence):
        """Tag the given ufal.udpipe.Sentence (inplace)."""
        self.model.tag(sentence, self.model.DEFAULT)

        
    def parse(self, sentence):
        """Parse the given ufal.udpipe.Sentence (inplace)."""
        self.model.parse(sentence, self.model.DEFAULT)

        
    def write(self, sentences, out_format):
        """Write given ufal.udpipe.Sentence-s in the required format (conllu|horizontal|vertical)."""
        output_format = OutputFormat.newOutputFormat(out_format)
        output = ''
        for sentence in sentences:
            output += output_format.writeSentence(sentence)
        output += output_format.finishDocument()
        return output
