# wiktionary_ipa_phoneme_lexicons
Helper script to generate free IPA phoneme lexicons from wiktionary.org, currently for German and English.

To run it, download a dump from wikitionary: https://dumps.wikimedia.org/dewiktionary/ (German) or https://dumps.wikimedia.org/enwiktionary/ (English) 

e.g. to get a German ipa lexicon from Wiktionary for ASR training, with removed stress markers, run:

    git clone https://github.com/bmilde/wiktionary_ipa_phoneme_lexicons
    cd wiktionary_ipa_phoneme_lexicons
    wget https://dumps.wikimedia.org/dewiktionary/latest/dewiktionary-latest-pages-articles-multistream.xml.bz2
    bunzip2 dewiktionary-latest-pages-articles-multistream.xml.bz2
    python3 make_lex.py -f -o de_ipa_lexicon.txt --remove-stress

The generated German phoneme lexicon should now be in de_ipa_lexicon.txt
