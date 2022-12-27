#!/bin/bash

python3 generate_conllu.py reldi-normtagner-sr/reldi-normtagner-sr.conllup -o reldi-normtagner-sr/reldi-normtagner-sr-train.conllu -d reldi-normtagner-sr-train -m NE
python3 generate_conllu.py reldi-normtagner-sr/reldi-normtagner-sr.conllup -o reldi-normtagner-sr/reldi-normtagner-sr-dev.conllu -d reldi-normtagner-sr-dev -m NE
python3 generate_conllu.py reldi-normtagner-sr/reldi-normtagner-sr.conllup -o reldi-normtagner-sr/reldi-normtagner-sr-test.conllu -d reldi-normtagner-sr-test -m NE
