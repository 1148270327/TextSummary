#!/usr/bin/python
# -*- coding:utf-8 -*-

"""
Predict Method for Testing
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import codecs

import numpy as np
from six.moves import xrange
import tensorflow as tf

from AiSummary import data_utils, eval
from AiSummary.headline import LargeConfig

config = LargeConfig()          # new Large Config, 
FLAGS = tf.app.flags.FLAGS      # Reuse the tf.app.flags from headline module

from AiSummary.headline import create_model
from AiSummary.headline import buckets
buckets = buckets

def decode():
  '''
  Manually input sentence interactively and the headline will be printed out
  '''
  with tf.Session() as sess:
    # Create model and load parameters.
    model = create_model(sess, True)
    model.batch_size = FLAGS.batch_size   #repeat single sentence 10 times as one batch  # We decode one sentence at a time.
    
    # Load vocabularies.
    vocab_path = os.path.join(FLAGS.data_dir,"vocab")
    vocab, rev_vocab = data_utils.initialize_vocabulary(vocab_path)
    
    # Decode from standard input interactively
    sys.stdout.write("> ")
    sys.stdout.flush()
    sentence = sys.stdin.readline()
    while sentence:
      if (len(sentence.strip('\n')) == 0):
        sys.stdout.flush()
        sentence = sys.stdin.readline()
      # Get token-ids for the input sentence.
      token_ids = data_utils.sentence_to_token_ids(tf.compat.as_bytes(sentence), vocab)
      # print (token_ids) # print token ids
      # Which bucket does it belong to?
      bucket_id = min([b for b in xrange(len(buckets)) if buckets[b][0] > len(token_ids)])
      # Get a 1-element batch to feed the sentence to the model.
      # print ("current bucket id" + str(bucket_id))
      encoder_inputs, decoder_inputs, target_weights = model.get_batch(
          {bucket_id: [(token_ids, [])]}, bucket_id)
      
      # Get output logits for the sentence.
      _, _, output_logits_batch = model.step(sess, encoder_inputs, decoder_inputs, target_weights, bucket_id, True)
      # This is a greedy decoder - outputs are just argmaxes of output_logits.     
      output_logits = []
      for item in output_logits_batch:
        output_logits.append(item[0])
      
      # print (output_logits)
      # print (len(output_logits))
      # print (output_logits[0])
      
      outputs = [int(np.argmax(logit)) for logit in output_logits]
      # If there is an EOS symbol in outputs, cut them at that point.
      if data_utils.EOS_ID in outputs:
        outputs = outputs[:outputs.index(data_utils.EOS_ID)]
      print(" ".join([tf.compat.as_str(rev_vocab[output]) for output in outputs]))
      print("> ", end="")
      sys.stdout.flush()
      sentence = sys.stdin.readline()

def generate_summary(input_dir, reference_dir, summary_dir):
  '''
    Args: 
      input_dir:     Dir of the main news content file, one per line, separated by space;
      reference_dir: Dir of the human summarized titles file, one title per line,
      summary_dir:   Generated headline summary will be saved to this location
    Return:
      None
  '''
  sentences = []  # input of 'str': news content
  references = [] # list of 'str':  news title
  summaries = []  # list of list:   predicted summary [[w11, w12, ...], [w21, w22,...]]
  
  input_file = codecs.open(input_dir, encoding='utf-8')
  for line in input_file:
    sentences.append(line.replace("\n","").encode('utf-8'))   # list of 'str', convert 'unicode' to 'str'
  
  reference_file = codecs.open(reference_dir, encoding='utf-8')
  for line in reference_file:
    references.append(line.replace("\n","").encode('utf-8'))   # list of 'str', convert 'unicode' to 'str'
  
  with tf.Session() as sess:
    # Create model and load parameters.
    model = create_model(sess, True)
    model.batch_size = FLAGS.batch_size
    
    # Load vocabularies.
    vocab_path = os.path.join(FLAGS.data_dir,"vocab")
    vocab, rev_vocab = data_utils.initialize_vocabulary(vocab_path)
    
    for i in range(len(sentences)):
      sentence = sentences[i]
      token_ids = data_utils.sentence_to_token_ids(tf.compat.as_bytes(sentence), vocab)
      bucket_id = min([b for b in xrange(len(buckets))
                       if buckets[b][0] > len(token_ids)])
      # Get a 1-element batch to feed the sentence to the model.
      encoder_inputs, decoder_inputs, target_weights = model.get_batch(
          {bucket_id: [(token_ids, [])]}, bucket_id)
      
      # Get output logits for the sentence.
      _, _, output_logits_batch = model.step(sess, encoder_inputs, decoder_inputs, target_weights, bucket_id, True)
      output_logits = []
      for item in output_logits_batch:
        output_logits.append(item[0])
      
      outputs = [int(np.argmax(logit)) for logit in output_logits]
      if data_utils.EOS_ID in outputs:
        outputs = outputs[:outputs.index(data_utils.EOS_ID)] # list of IDs
      
      summary = [tf.compat.as_str(rev_vocab[output]) for output in outputs]
      summaries.append(summary)
      print(" ".join(summary))
      
      # Evaluate ROUGE-N score, compare summary and reference, both are 'str' object in py2 or 'bytes' in py3
      reference = []
      reference.append([tf.compat.as_str(w) for w in references[i].split(" ")])
      score = eval.evaluate(summary, reference, method ="rouge_n", n = 2)
      print ("Evaludated Rouge-2 score is %.4f" % score)
  
  # Write Output to summary_dir
  summary_file = codecs.open(summary_dir, 'w', encoding='utf-8')
  for summary in summaries:
    line = " ".join(summary) + b"\n" # 'str' in 'utf-8' coding
    summary_file.write(line.decode('utf-8')) # write unicode to file

def main(_):
  if (len(sys.argv)==1):
    # 0 other args: type in news content interactively
    decode()
  
  else:
    # 3 other args: input_dir, reference_dir, summary_dir
    input_dir = sys.argv[1]
    reference_dir = sys.argv[2]
    summary_dir = sys.argv[3]
    print ('input_dir %s' % input_dir)
    print ('reference_dir %s' % reference_dir)
    print ('summary_dir %s' % summary_dir)
    
    generate_summary(input_dir, reference_dir, summary_dir)
    
    #input_dir = os.path.join(FLAGS.data_dir,"test/content-test.txt")
    #reference_dir = os.path.join(FLAGS.data_dir,"test/title-test.txt")
    #summary_dir = os.path.join(FLAGS.data_dir,"test/summary.txt")

if __name__ == "__main__":
  tf.app.run()
