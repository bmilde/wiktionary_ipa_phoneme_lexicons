# -*- coding: utf-8 -*-
from __future__ import print_function

import io
import argparse
import re
from collections import defaultdict

#      <text xml:space="preserve">== Distributionsklasse ({{Sprache|Deutsch}}) ==

# words containing these strings are ignored
wordfilter = ['{','}','[',']','PAGENAME','&lt','&gt','&amp','|','/',' ',':', '*']

def clean_word(word):
    rules = [(',',''),('?',''),('!',''),('.',''),(u'®','')]
    for rule in rules:
        word = word.replace(rule[0],rule[1])
    return word

def remove_stress(phonemes):
    return phonemes.replace(u'ˈ','').replace(u'ˌ','')

def process(wikifile, gen_testset, do_remove_stress, lang):
    lang_count = defaultdict(int)
    written_out = 0
    with io.open(wikifile,'r',encoding='utf-8') as wiki_in:
        with io.open(wikifile+'.lex','w',encoding='utf-8') as wiki_out:
            found_word=False
            for line in wiki_in:
                if line[-1] == '\n':
                    line = line[:-1]
                line = line.strip()
                #match = re.match('\<text xml:space="preserve"\>== (.*) \(\{\{Sprache\|Deutsch\}\}\) ==', line.strip())
                
                if lang == 'de':
                    match = re.match('.*==(.*)\(\{\{Sprache\|Deutsch\}\}\) ==', line.strip())
                elif lang == 'en':
                    match = re.match('<title>(.*)<\/title>', line.strip())

                if ('==English==' in line):
                    found_english=True

                if match:
                    word = match.group(1)
                    word = word.strip()
                    #print(word)
                    if not any((elem in word for elem in wordfilter)):
                        if len(word) > 20:
                            print(word)
                        if len(word) > 1 and not word[-1]=='-' and not word[0]=='-':
                            word_cleaned = clean_word(word)
                            #print line
                            #print word_cleaned
                            found_word=True

                if lang=='de':
                    match = re.match('^\:\{\{IPA\}\}.{1,3}\{\{Lautschrift\|([^\}]+)\}\}.*',  line.strip())
                elif lang=='en':
                    #* {{a|US}} {{IPA|/ə.bɹʌpt/|/aˈbɹʌpt/|lang=en}}
                    #match = re.match('^\* {0,4}\{\{a\|US\}\} {0,4}\{\{IPA.{0,4}\|\/?([^\/\}\|]+)\/?\||\}.*',  line.strip())
                    #match = re.match('^\* {0,4}(?:\{\{a\|([^\/\}\|]+)\}\})? {0,4}\{\{IPA.{0,4}\|\/?([^\/\}\|]+)\/?\||\}.*', line.strip())
                    match = None
                    if 'lang=en' in line and 'IPA' in line and not 'RP' in line and not 'UK' in line:
                        match = re.match('[^\/]*\/([^\/]*)\/[^\/]*', line.strip())

                if found_word and match:
                    #if lang=='en' and not found_english:
                    #    continue
                    phonemes = match.group(1)
                    #phonemes = None
                    #if lang=='de':
                    #    phonemes = match.group(1)
                    #elif lang=='en':
                    #    lang_count[match.group(1)] += 1
                    #    if match.group(1) is None or match.group(1) in ['US','GenAM','USA']: # US dialect.For UK: UK or RP (Received Pronunciation).
                    #        phonemes = match.group(2)
                    #        if len(word) > 20:
                    #            print match.group(2)
                    #print phonemes
                    if phonemes is not None and found_word: 
                        if (not u'…' in phonemes) and (not '...' in phonemes):
                            if remove_stress:
                                phonemes = remove_stress(phonemes)
                            phonemes = phonemes.replace(' ','').replace('.','').replace('(','').replace(')','').replace('[','').replace(']','')
                            #if word == 'du':
                            #    print line
                            #    print phonemes
                            wiki_out.write(word_cleaned+u' '+u' '.join(phonemes)+'\n')
                            written_out += 1
                            if (written_out%1000 == 0):
                                print('written: ', written_out, 'entries.')
                        #found_word=False
                        #found_english=False
                if '=See also=' in line or '=Translations=' in line or '</page>' in line or '{{Beispiele}}' in line or '{{Referenzen}}' in line or '{{Quellen}}' in line:
                    found_word=False
                    found_english=False

#    print('lang count')
#    print(lang_count)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process a wiktionary dictionary in xml format and make a text ipa lexicon.')
    parser.add_argument('-f', '--file', dest='file', help='process this xml wiktionary lexicon file', type=str, default='../data/dewiktionary-20170120-pages-articles-multistream.xml')
    parser.add_argument('-o', '--outfile', dest='outfile', help='lexicon out file', type=str, default='de_ipa_lexicon.txt')
    parser.add_argument('-t', '--gen-testset', dest='gen_testset', help='generate a testset', action='store_true', default=False)
    parser.add_argument('-r', '--remove-stress', dest='remove_stress', help='remove stress markers',  action='store_true', default=False)
    parser.add_argument('-l', '--lang', dest='lang', help='language specific parsing', default = 'de')
    args = parser.parse_args()
    process(args.file, args.gen_testset, args.remove_stress, args.lang)
