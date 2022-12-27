#!/bin/bash

python3 generate_conllu.py reldi-normtagner-hr/reldi-normtagner-hr.conllup -o reldi-normtagner-hr/reldi-normtagner-hr-train.conllu -d reldi-normtagner-hr-train -m NE
python3 generate_conllu.py reldi-normtagner-hr/reldi-normtagner-hr.conllup -o reldi-normtagner-hr/reldi-normtagner-hr-dev.conllu -d reldi-normtagner-hr-dev -m NE
python3 generate_conllu.py reldi-normtagner-hr/reldi-normtagner-hr.conllup -o reldi-normtagner-hr/reldi-normtagner-hr-test.conllu -d reldi-normtagner-hr-test -m NE
