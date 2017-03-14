#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Holds common configuration parameters

@author: yaric
"""

# The root path to the data directory
data_dir = "../data"
# The output directory
out_dir = "../out"
# The intermediate output directory
intermediate_dir = out_dir + "/intermediate" 
# The directory to store unit test results
unit_tests_dir = intermediate_dir + "/u_tests"
# The directory to store rained models
models_dir = intermediate_dir + "/models"

#
# The train raw corpora
#
sentence_train_path = data_dir + "/sentence_train.txt"
parse_train_path = data_dir + "/parse_train.txt"
glove_train_path = data_dir + "/glove_train.txt"
corrections_train_path = data_dir + "/corrections_train.txt"
pos_tags_train_path = data_dir + "/pos_tags_train.txt"

#
# The validate raw corpora
#
sentence_validate_path = data_dir + "/sentence_test.txt"
parse_validate_path = data_dir + "/parse_test.txt"
glove_validate_path = data_dir + "/glove_test.txt"
corrections_validate_path = data_dir + "/corrections_test.txt"
pos_tags_validate_path = data_dir + "/pos_tags_test.txt"

#
# The test raw corpora
#
sentence_test_path = data_dir + "/sentence_private_test.txt"
parse_test_path = data_dir + "/parse_private_test.txt"
glove_test_path = data_dir + "/glove_private_test.txt"
pos_tags_test_path = data_dir + "/pos_tags_private_test.txt"

#
# The train processed corpora
#
train_features_path = intermediate_dir + "/train_features.npy"
train_labels_path = intermediate_dir + "/train_labels.npy"

#
# The validate processed corpora
#
validate_features_path = intermediate_dir + "/validate_features.npy"
validate_labels_path = intermediate_dir + "/validate_labels.npy"

#
# The test processed corpora
#
test_features_path = intermediate_dir + "/test_features.npy"
test_labels_prob_path = intermediate_dir + "/test_labels_prob.npy"

# The test results file
test_reults_path = out_dir + "/submission_test.txt"