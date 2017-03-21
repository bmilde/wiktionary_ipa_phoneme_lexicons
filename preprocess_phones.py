#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import argparse
import io
import re

def removestress(line):
  return line.replace('0','').replace('1','').replace('2','').replace('3','')

def process(srctrains, devfrac, srckeys, multitrain=False, lowercasewords=False):

  lines = []
  for i,lexicon_file in enumerate(srctrains):
    with io.open(lexicon_file, 'r', encoding='utf-8') as src:
      if multitrain:
        lines += [srckeys[i]+' '+line for line in src.readlines()]
      else:  
        lines += src.readlines()
  
  if devfrac>0.0:
    goal_num = float(len(lines)) * args.devfrac
    modulo_n = int(float(len(lines)) / goal_num + 0.5)
  else:
    modulo_n = -1

  print('modulo_n for the dev set is:', modulo_n)

  with  io.open(srctrains[0]+'.words','w',encoding='utf-8') as dst_words, io.open(srctrains[0]+'.phonemes','w',encoding='utf-8') as dst_phones, \
          io.open(srctrains[0]+'.dev.words','w',encoding='utf-8') as dst_dev_words, io.open(srctrains[0]+'.dev.phonemes','w',encoding='utf-8') as dst_dev_phones, \
          io.open(srctrains[0]+'.orig.dev','w',encoding='utf-8') as orig_dev, io.open(srctrains[0]+'.orig','w',encoding='utf-8') as orig:
    for i,line in enumerate(lines):
#      print line
      if line[-1]=='\n':
        line = line[:-1]
      #ingore alternate pronounciations for now (e.g. CMU sphix lexicon)
      if '(' in line and ')' in line:
        continue

      split = line.split()

      # Opennmt and  expects space separeted tokens. We also space seperate the letters in a word, e.g. word -> w o r d
      if multitrain:
        word = split[0] + ' ' + ' '.join(split[1])
        singleword = split[1]
        if split[0] == '_EN' or lowercasewords:
          phones = removestress(' '.join(split[2:]))
          word = split[0] + ' ' + ' '.join(split[1]).lower()
          singleword = split[1].lower()
        else:
          phones = ' '.join(split[2:])
      else:
        word = ' '.join(split[0])
        phones = ' '.join(split[1:])

      #Matches phonolox inline multiword, e.g. FriedrichHain, we ignore those too.
      if re.match(u'[A-ZÖÜÄ]+[a-zöüäß]{2,}[A-ZÖÜÄ]+.+', singleword.replace(' ','')):
        print('Ignoring', word.replace(' ',''))  
        continue
      
      if( devfrac>0.0 and i%modulo_n == 0):
        dst_dev_words.write(word+'\n')
        dst_dev_phones.write(phones+'\n')
        orig_dev.write(singleword + ' ' + phones)
      else:
        dst_words.write(word+'\n')
        dst_phones.write(phones+'\n')
        orig.write(singleword + ' ' + phones)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Preparing a phoneme lexicon in CMU sphinx format for https://github.com/harvardnlp/seq2seq-attn or OpenNMT')
  parser.add_argument('--srctrain', help="Input train lexicon", type=str, default='train_manual.lex')
  parser.add_argument('--multitrain', help="Comma seperated list of input lexicons", type=str, default='')
  parser.add_argument('--multitrainkeys', help="Comma seperated list of input lexicon tokens to use for multi training", type=str, default='')
  parser.add_argument('--devfrac', help="The fraction to use for development corpus", type=float, default=0.0)
  parser.add_argument('--lowercasewords', help="If set, lowercase all words in the lexicon (useful for CMUDict)", action='store_true', default=False)
  args = parser.parse_args()

  multitrain = False
  
  srctrains = []
  srckeys = []

  # check if we do multitask learning:
  if args.multitrain != '':
    srctrains = args.multitrain.split(',')
    multitrain = True
  else:
    srctrains = [args.srctrain]

  if args.multitrainkeys != '':
    srckeys = args.multitrainkeys.split(',')

  process(srctrains, args.devfrac, srckeys, multitrain, args.lowercasewords)
