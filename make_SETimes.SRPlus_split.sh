#!/bin/bash

python3 generate_conllu.py SETimes.SRPlus/set.sr.plus.conllup -o SETimes.SRPlus/set.sr.plus-train.conllu -d set.sr.plus-train -m NE
python3 generate_conllu.py SETimes.SRPlus/set.sr.plus.conllup -o SETimes.SRPlus/set.sr.plus-dev.conllu -d set.sr.plus-dev -m NE
python3 generate_conllu.py SETimes.SRPlus/set.sr.plus.conllup -o SETimes.SRPlus/set.sr.plus-test.conllu -d set.sr.plus-test -m NE
