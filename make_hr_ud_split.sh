#!/bin/bash

python3 generate_conllu.py hr500k/hr500k.conllup -o hr500k/hr_set-ud-train.conllu -d hr_set-ud-train
python3 generate_conllu.py hr500k/hr500k.conllup -o hr500k/hr_set-ud-dev.conllu -d hr_set-ud-dev
python3 generate_conllu.py hr500k/hr500k.conllup -o hr500k/hr_set-ud-test.conllu -d hr_set-ud-test
