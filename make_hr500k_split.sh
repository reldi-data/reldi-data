#!/bin/bash

python3 generate_conllu.py hr500k/hr500k.conllup -o hr500k/hr500k-train.conllu -d hr500k-train
python3 generate_conllu.py hr500k/hr500k.conllup -o hr500k/hr500k-dev.conllu -d hr500k-dev
python3 generate_conllu.py hr500k/hr500k.conllup -o hr500k/hr500k-test.conllu -d hr500k-test
