# reldi-data
This repository contains tools and scripts for validating, curating, and maintaining ReLDI datasets.

## Introduction
After quite some time of struggling with different corpus formats and numerous non-reusable conversion scripts that were difficult to maintain, it has been decided that .conllup will become the main format for all ReLDI corpora. All other formats will be generated from this one as it holds most information. Other formats will not be version-tracked from this point forward.

Unification of the format also allows for generalizing the tools for validating, curating, and maintaining corpora.

Although all ReLDI corpora are version-tracked in separate repositories, this toolset is meant also as an entry point to these corpora. For this reason, all corpora, along with some other useful packages, are included in this repository as [submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules).

## Instalation
1. Clone this repository
```
git clone git@github.com:reldi-data/reldi-data.git
```
2. Retrieve all submodules
```
git submodule init
git submodule update
```

3. Create python 3 based virtualenv or pyenv
4. Install dependencies
```
pip install -r requirements.txt
```

Periodically check for submodule updates.
```
git submodule update --remote
```

## Usage

### Generating .conllu from .conllup
Use `generate_conllu.py`.

```
(virtualenv) $ python3 generate_conllu.py -h
usage: CONLLU corpus generator [-h] [-o OUTPUT_FILE]
                               [-d [DATASETS [DATASETS ...]]]
                               [-t [OMIT_DATASETS [OMIT_DATASETS ...]]]
                               [-a [ANNOTATIONS [ANNOTATIONS ...]]]
                               [-n [OMIT_ANNOTATIONS [OMIT_ANNOTATIONS ...]]]
                               [-m [MISC [MISC ...]]] [--keep-status-metadata]
                               source

Generates corpus in .conllu format from .conllup source

positional arguments:
  source                Path to the source file.

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT_FILE        Path to the output file. (default: None)
  -d [DATASETS [DATASETS ...]], --datasets [DATASETS [DATASETS ...]]
                        Filter documents by containment in datasets. (default:
                        [])
  -t [OMIT_DATASETS [OMIT_DATASETS ...]], --omit-datasets [OMIT_DATASETS [OMIT_DATASETS ...]]
                        Filter documents by not being contained in datasets.
                        (default: [])
  -a [ANNOTATIONS [ANNOTATIONS ...]], --annotations [ANNOTATIONS [ANNOTATIONS ...]]
                        Filter documents by level of annotation. (default: [])
  -n [OMIT_ANNOTATIONS [OMIT_ANNOTATIONS ...]], --omit-annotations [OMIT_ANNOTATIONS [OMIT_ANNOTATIONS ...]]
                        Filter documents by not having certain level of
                        annotation. (default: [])
  -m [MISC [MISC ...]], --misc [MISC [MISC ...]]
                        Transfer data from these columns to MISC. (default:
                        [])
  --keep-status-metadata
                        Write document status metadata to output file.
                        (default: False)
```

### Validating .conllup format
Use `validate_conllup.py`.

```
(virtualenv) $ python3 validate_conllup.py -h
usage: CONLLUP corpus validator [-h] [--quiet] [--max-err MAX_ERR] --lang LANG
                                [--level LEVEL] [--multiple-roots]
                                [--no-tree-text] [--no-space-after] [--coref]
                                input

Validates corpus in .conllup

optional arguments:
  -h, --help         show this help message and exit

Input / output options:
  --quiet            Do not print any error messages. Exit with 0 on pass,
                     non-zero on fail. (default: False)
  --max-err MAX_ERR  How many errors to output before exiting? 0 for all.
                     Default: 20.
  input              Path to the source .conllup file.

Tag sets:
  Options relevant to checking tag sets.

  --lang LANG        Which langauge are we checking? If you specify this (as a
                     two-letter code), the tags will be checked using the
                     language-specific files in the data/ directory of the
                     validator. (default: None)
  --level LEVEL      Level 1: Test only CoNLL-U backbone. Level 2: UD format.
                     Level 3: UD contents. Level 4: Language-specific labels.
                     Level 5: Language-specific contents. (default: 5)

Tree constraints:
  Options for checking the validity of the tree.

  --multiple-roots   Allow trees with several root words (single root required
                     by default). (default: True)

Metadata constraints:
  Options for checking the validity of tree metadata.

  --no-tree-text     Do not test tree text. For internal use only, this test
                     is required and on by default. (default: True)
  --no-space-after   Do not test presence of SpaceAfter=No. (default: True)

Coreference / entity constraints:
  Options for checking coreference and entity annotation.

  --coref            Test coreference and entity-related annotation in MISC.
                     (default: False)
```

### Validating .conllup format of ReLDI corpora using predefined and currently appropriate settings
```
$ source validate_SETimes.SRPlus.sh
```
or
```
$ source validate_hr500k.sh
```
or
```
$ source validate_reldi-normtagner-hr.sh
```
or
```
$ source validate_reldi-normtagner-sr.sh
```
Compare validation results with README.validation.md files in respective corpus repositories.

### Validating XPOS to UPOS+Feats mapping
Use `check_xpos_upos_feats.py`

```
(virtualenv) $ python3 check_xpos_upos_feats.py -h
usage: CONLLUP tag mapping validator [-h] [-o OUTPUT_FILE] source

Validates mapping of XPOS to UPOS+Feats tags in a CONLLUP corpus.

positional arguments:
  source                Path to the source file.

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT_FILE, --output OUTPUT_FILE
                        Path to the output file. (default: None)

```
If the OUTPUT_FILE parameter is not provided, by default the output filename is set to `./<source path>/<source basename>.uposxpos.txt`.

Detected mismatches are printed to stdout so you can pipe the command to `sort` and `uniq -c` to get the aggregated stats.

Compare aggregated validation results with README.validation.md files in respective corpus repositories.

Mismatches can also be analized in-place by searching for `UPOS!!!` and `XPOS!!!` in the output file.

#### Example
```
(virtualenv) $ python3 check_xpos_upos_feats.py SETimes.SRPlus/set.sr.plus.conllup | sort | uniq -c
     33 UPOS Rgc UposTag=DET|Degree=Cmp
     31 UPOS Rgp UposTag=DET|Degree=Pos
      8 UPOS Rgp UposTag=DET|Degree=Pos|PronType=Dem
     69 UPOS Rgp UposTag=DET|Degree=Pos|PronType=Ind
      7 UPOS Rgp UposTag=DET|Degree=Pos|PronType=Int,Rel
      1 UPOS Rgs UposTag=DET|Degree=Sup
      9 UPOS Y UposTag=ADJ|_
      7 UPOS Y UposTag=NOUN|_
      3 UPOS Y UposTag=PART|_
      4 UPOS Y UposTag=PROPN|_
      1 UPOS Y UposTag=PUNCT|_
```


### Creating the official UD split

```
$ source make_hr_ud_split.sh
```
or
```
$ source make_sr_ud_split.sh
```

### Creating arbitrary train-dev-test split
Use `make_train_dev_test_split.py`.

```
(virtualenv) $ python3 make_train_dev_test_split.py -h
usage: CONLLUP corpus splitter [-h] [-o OUTPUT_FOLDER] [-f OUTPUT_FILENAME]
                               [--keep-conllu] [-e [DATASETS [DATASETS ...]]]
                               [-i [OMIT_DATASETS [OMIT_DATASETS ...]]]
                               [-a [ANNOTATIONS [ANNOTATIONS ...]]]
                               [-n [OMIT_ANNOTATIONS [OMIT_ANNOTATIONS ...]]]
                               [-m [MISC [MISC ...]]] [--keep-status-metadata]
                               [-t TEST] [-d DEV] [-s SEED]
                               [--cross-validation]
                               source

Generates .conllu corpus from .conllup source and splits it reproducibly into
train, dev and test set.

optional arguments:
  -h, --help            show this help message and exit

Input / output options:
  source                Path to the source .conllup file.
  -o OUTPUT_FOLDER      Path to the output folder. (default: None)
  -f OUTPUT_FILENAME, --output-filename OUTPUT_FILENAME
                        Specify the filename for output files. (default: None)
  --keep-conllu         Keep intermediate .conllu file. (default: True)

.conllu generation options:
  -e [DATASETS [DATASETS ...]], --datasets [DATASETS [DATASETS ...]]
                        Filter documents by containment in datasets. (default:
                        [])
  -i [OMIT_DATASETS [OMIT_DATASETS ...]], --omit-datasets [OMIT_DATASETS [OMIT_DATASETS ...]]
                        Filter documents by not being contained in datasets.
                        (default: [])
  -a [ANNOTATIONS [ANNOTATIONS ...]], --annotations [ANNOTATIONS [ANNOTATIONS ...]]
                        Filter documents by level of annotation. (default: [])
  -n [OMIT_ANNOTATIONS [OMIT_ANNOTATIONS ...]], --omit-annotations [OMIT_ANNOTATIONS [OMIT_ANNOTATIONS ...]]
                        Filter documents by not having certain level of
                        annotation. (default: [])
  -m [MISC [MISC ...]], --misc [MISC [MISC ...]]
                        Transfer data from these columns to MISC. (default:
                        [])
  --keep-status-metadata
                        Write document status metadata to output file.
                        (default: False)

Split options:
  -t TEST, --test TEST  Test set size. (default: 0.3)
  -d DEV, --dev DEV     Dev set size. (default: 0.0)
  -s SEED, --seed SEED  Manually set random seed. (default: None)
  --cross-validation    Create k-fold cross-validation datasets. (default:
                        False)
```

### Creating reproducible train-dev-test corpora split

```
$ source make_hr500k_split.sh
```
or
```
$ source make_SETimes.SRPlus_split.sh
```
or
```
$ source make_reldi-normtagner-hr_split.sh
```
or
```
$ source make_reldi-normtagner-sr_split.sh
```
