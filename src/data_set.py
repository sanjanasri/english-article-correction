#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The data set generator. It will create numeric features matrix by chunking Noun 
Phrases (NP) from provided data corpus and substituting words in the NP with
corresponding indices from Glove vectors.

@author: yaric
"""
from enum import IntEnum
import numpy as np
import os

import tree_dict as td
import utils
import config

# The Part-of-Speech enumerations
class POS(IntEnum):
    CC = 1
    CD = 2
    DT = 3
    EX = 4
    FW = 5
    IN = 6
    JJ = 7
    JJR = 8
    JJS = 9
    LS = 10
    MD = 11
    NN = 12
    NNS = 13
    NNP = 14
    NNPS = 15
    PDT = 16
    POS = 17
    PRP = 18
    PRP_ = 19
    RB = 20
    RBR = 21
    RBS = 22
    RP = 23
    SYM = 24
    TO = 25
    UH = 26
    VB = 27
    VBD = 28
    VBG = 29
    VBN = 30
    VBP = 31
    VBZ = 32
    WDT = 33
    WP = 34
    WP_ = 35
    WRB = 36
    
    @classmethod
    def valueByName(cls, name):
        """
        Find enum value by the name
        Raise:
            exception in case if the name not found
        """
        return cls.__members__[name].value
    
    @classmethod
    def hasPOSName(cls, name):
        """
        Finds if provided name is known as POS
        """
        return name in cls.__members__

# The determinant article labels enumeration
class DT(IntEnum):
    A = 1
    AN = 2
    THE = 3
    
    @classmethod
    def valueByName(cls, name):
        """
        Find enum value by the name
        Raise:
            exception in case if the name not found
        """
        return cls.__members__[name.upper()].value

# The offset for POS features start    
offset = 2
# The number of features extracted
n_features = offset + len(POS.__members__) + 1

def extractFeatures(node, text, glove, corrections = None):
    """
    Method to extract features from provided node and store it in features array
    Arguments:
        node: the parse tree node with sentence
        text: the text corpora to extract features from
        glove: the glove indices map
        corrections: the list of corrections [optional] if building training data set
    Return:
        tuple with array of features for found determiner phrases with articles and
        labels or None
    """
    """
    Features map:
    DT glove index | NN(S) glove index | units between DTa and NN | 
    CC | CD | DT | EX | FW | IN | JJ | JJR | JJS| LS | MD | NN | NNS | NNP | NNPS | PDT	| POS | PRP | PRP$ | RB | RBR | RBS | RP | SYM
    TO | UH | VB | VBD | VBG | VBN | VBP | VBZ | WDT | WP | WP$ | WRB
    """
    labels = None
    
    dpa_subtrees = node.dpaSubtrees()
    features = np.zeros((len(dpa_subtrees), n_features), dtype = 'f')
    if corrections != None:
        labels = np.zeros((len(dpa_subtrees), 1), dtype = 'int')
        
    # collect features
    row = 0
    for st in dpa_subtrees:
        dta_node = None
        nn_node = None
        for node in st.leaves():
            # collect POS type
            pos_name = node.pos.replace("$", "_")
            if POS.hasPOSName(pos_name):
                pos_index = POS.valueByName(pos_name)
                features[row, offset + pos_index] += 1
            
            if node.pos == 'DT' and any(node.name == name for name in ['a', 'an', 'the']):
                # found DT with article
                features[row, 0] = glove[node.s_index]
                dta_node = node
                # store correction label if appropriate
                if corrections[node.s_index] != None:
                    labels[row] = DT.valueByName(corrections[node.s_index])
                    
            elif nn_node == None and any(node.pos == pos for pos in ['NN', 'NNS', 'NNP', 'NNPS']):
                # found first (proper) noun
                features[row, 1] = glove[node.s_index]
                nn_node = node
             
            # store distance between DT and NN(PS)
            if dta_node != None and nn_node != None:
                features[row, 2] = abs(dta_node.s_index - nn_node.s_index)
                
        # increment row index
        row += 1
        
    return (features, labels)
            
    

def create(corpus_file, parse_tree_file, glove_file, corrections_file, test = False):
    """
    Creates new data set from provided files
    Arguments:
        corpus_file: the file text corpus
        parse_tree_file: the file with constituency parse trees build over data corpus
        glove_file: the file with GloVe vectors indexes for data corpus
        corrections_file: the file with labeled corrections
        test: the flag to indicate whether test data set should be constructed
    Return:
        (features, labels): the tuple with features and labels. If test parameter is True then labels
        wil be None
    """
    text_data = utils.read_json(corpus_file)
    parse_trees_list = utils.read_json(parse_tree_file)
    glove_indices = utils.read_json(glove_file)
    
    if test == False:
        corrections = utils.read_json(corrections_file)
    
    # The sanity checks
    #
    if len(text_data) != len(parse_trees_list):
        raise Exception("Text data corpora lenght: %d, not equals to the parse trees count: %d" 
                        % (len(text_data), len(parse_trees_list)))
    if test == False and len(corrections) != len(parse_trees_list):
        raise Exception("Corrections list lenght: %d, not equals to the parse trees count: %d" 
              % (len(corrections), len(parse_trees_list)))
    if len(glove_indices) != len(parse_trees_list):
        raise Exception("Glove indices list lenght: %d, not equals to the parse trees count: %d" 
              % (len(corrections), len(parse_trees_list)))
    
    # iterate over constituency parse trees and extract features
    features = None
    labels = None
    index = 0
    corrected_sentences = 0
    for tree_dict in parse_trees_list:
        # get corrections list for the sentence
        if test == False:
            s_corr = corrections[index]
        else:
            s_corr = None
        # get glove indices list for the sentence
        g_list = glove_indices[index]
        # get text corpora list for sentence
        t_list = text_data[index]
        # get parse tree for sentence
        tree, _ = td.treeFromDict(tree_dict)

        # do sanity checks
        #
        leaves = tree.leaves()
        if test == False and len(s_corr) != len(leaves):
            raise Exception("Corrections list lenght: %d not equal the tree leaves count: %d at index: %d" 
                            % (len(s_corr), len(leaves), index))
        if len(g_list) != len(leaves):
            raise Exception("Glove indices list lenght: %d not equal the tree leaves count: %d at index: %d" 
                            % (len(g_list), len(leaves), index))
        if len(t_list) != len(leaves):
            raise Exception("Text corpora list lenght: %d not equal the tree leaves count: %d at index: %d" 
                            % (len(t_list), len(leaves), index))
        
        # check if sentence has corrections
        #
        if test == False and any(w != None for w in s_corr):
            corrected_sentences += 1
            
        # generate features and labels
        #
        f, l = extractFeatures(node = tree, text = t_list, glove = g_list, corrections = s_corr)
        if index == 0:
            features = f
        else:
            features = np.concatenate((features, f), axis=0)
        
        if index == 0:
            labels = l
        elif test == False:
            labels = np.concatenate((labels, l), axis = 0)
        
        index += 1
        
        
    print("Features collected: %d" % (len(features)))
    
    return (features, labels)
        
        
if __name__ == '__main__':
    # Clean output directory
    if os.path.exists(config.intermediate_dir):
        os.removedirs(config.intermediate_dir)
        
    os.makedirs(config.intermediate_dir)
    
    # Create train data corpus
    #
    print("Making train features")
    features, labels = create(corpus_file = config.sentence_train_path, 
                             parse_tree_file = config.parse_train_path,
                             glove_file = config.glove_train_path, 
                             corrections_file = config.corrections_train_path)
    np.save(config.train_features_path, features)
    np.save(config.train_labels_path, labels)
    
    # Create validate data corpus
    #
    print("Making validate features")
    features, labels = create(corpus_file = config.sentence_validate_path, 
                             parse_tree_file = config.parse_validate_path,
                             glove_file = config.glove_validate_path, 
                             corrections_file = config.corrections_validate_path)
    np.save(config.validate_features_path, features)
    np.save(config.validate_labels_path, labels)
    
    # Create test data features
    #
    print("Making test features")
    features, _ = create(corpus_file = config.sentence_validate_path, 
                             parse_tree_file = config.parse_validate_path,
                             glove_file = config.glove_validate_path, 
                             corrections_file = config.corrections_validate_path,
                             test = True)
    np.save(config.test_features_path, features)
