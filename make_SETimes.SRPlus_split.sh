#!/bin/bash

python3 make_train_dev_test_split.py SETimes.SRPlus/set.sr.plus.conllup -o SETimes.SRPlus -a UD -t 0.2 -d 0.1 -s 27
