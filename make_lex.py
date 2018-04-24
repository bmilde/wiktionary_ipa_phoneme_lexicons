# -*- coding: utf-8 -*-
from __future__ import print_function

import io
import argparse
import re
from collections import defaultdict

# words containing these strings are ignored
wordfilter = ['{','}','[',']','PAGENAME','&lt','&gt','&amp','|','/',' ',':', '*']

def clean_word(word):
    rules = [(',',''),('?',''),('!',''),('.',''),(u'®','')]
    for rule in rules:
        word = word.replace(rule[0],rule[1])
    return word

def remove_stress(phonemes):
    return phonemes.replace(u'ˈ','').replace(u'ˌ','')

def process(wikifile, outfile, gen_testset, do_remove_stress, lang):
    lang_count = defaultdict(int)
    written_out = 0
    with io.open(wikifile,'r',encoding='utf-8') as wiki_in:
        with io.open(outfile,'w',encoding='utf-8') as wiki_out:
            found_word=False
            for line in wiki_in:
                if line[-1] == '\n':
                    line = line[:-1]
                line = line.strip()
               
                # start segment for the dictionary entry
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
                            found_word=True

                # regex to identify IPA entry
                if lang=='de':
                    match = re.match('^\:\{\{IPA\}\}.{1,3}\{\{Lautschrift\|([^\}]+)\}\}.*',  line.strip())
                elif lang=='en':
                    #entries are various of this line: * {{a|US}} {{IPA|/ə.bɹʌpt/|/aˈbɹʌpt/|lang=en}}
                    match = None
                    if 'lang=en' in line and 'IPA' in line and not 'RP' in line and not 'UK' in line:
                        match = re.match('[^\/]*\/([^\/]*)\/[^\/]*', line.strip())

                if found_word and match:
                    phonemes = match.group(1)
                    # we identified the word for entry and could parse the phoneme entry:
                    if phonemes is not None and found_word: 
                        if (not u'…' in phonemes) and (not '...' in phonemes):
                            if remove_stress:
                                phonemes = remove_stress(phonemes)
                            phonemes = phonemes.replace(' ','').replace('.','').replace('(','').replace(')','').replace('[','').replace(']','')
                            wiki_out.write(word_cleaned+u' '+u' '.join(phonemes)+'\n')
                            written_out += 1
                            if (written_out%1000 == 0):
                                print('written: ', written_out, 'entries.')
                # If we see this somewhere in our input, we are already past the phoneme entry
                if '=See also=' in line or '=Translations=' in line or '</page>' in line or '{{Beispiele}}' in line or '{{Referenzen}}' in line or '{{Quellen}}' in line:
                    found_word=False
                    found_english=False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process a wiktionary dictionary in xml format and make a text ipa lexicon. Currently for German and English wiktionary XMLs.')
    parser.add_argument('-f', '--file', dest='file', help='process this xml wiktionary lexicon file', type=str, default='dewiktionary-latest-pages-articles-multistream.xml')
    parser.add_argument('-o', '--outfile', dest='outfile', help='lexicon out file', type=str, default='de_ipa_lexicon.txt')
    parser.add_argument('-t', '--gen-testset', dest='gen_testset', help='generate a testset', action='store_true', default=False)
    parser.add_argument('-r', '--remove-stress', dest='remove_stress', help='remove stress markers',  action='store_true', default=False)
    parser.add_argument('-l', '--lang', dest='lang', help='language specific parsing', default = 'de')
    args = parser.parse_args()
    process(args.file, args.outfile, args.gen_testset, args.remove_stress, args.lang)
