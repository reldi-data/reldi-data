#!/bin/bash

python3 generate_conllu.py SETimes.SRPlus/set.sr.plus.conllup -o SETimes.SRPlus/sr_set-ud-train.conllu -d sr_set-ud-train
python3 generate_conllu.py SETimes.SRPlus/set.sr.plus.conllup -o SETimes.SRPlus/sr_set-ud-dev.conllu -d sr_set-ud-dev
python3 generate_conllu.py SETimes.SRPlus/set.sr.plus.conllup -o SETimes.SRPlus/sr_set-ud-test.conllu -d sr_set-ud-test
