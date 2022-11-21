#!/bin/bash

python3 make_train_dev_test_split.py hr500k/hr500k.conllup -o hr500k -a UD -t 0.2 -d 0.1 -s 15
