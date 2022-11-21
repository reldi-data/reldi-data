import argparse
import os
import re

from collections import namedtuple, OrderedDict
from io import StringIO


DATASETS_RE = re.compile(r'(?<=(?:# contained_in_datasets = ))(.+)(?=\n)')
ANNOTATIONS_RE = re.compile(r'(?<=(?:# annotation_levels = ))(.+)(?=\n)')

CORPUS_NULL_VALUES = ['_', '*']


class CONLLUPToken(namedtuple('CONLLUPToken', ['index', 'form', 'lemma', 'upos', 'msd', 'upos_feats', 'head', 'deprel',
                                               'deps', 'misc', 'ne', 'dp', 'srl', 'rmisc'])):
    @staticmethod
    def create_from_conllup_line(line):
        line = line.split('\t')
        if line[9] == '_':
            misc = []
        else:
            misc = line[9].split('|')
        misc = OrderedDict([tuple(v.split('=')) for v in misc])
        if line[13] == '_':
            rmisc = []
        else:
            rmisc = line[13].split('|')
        rmisc = OrderedDict([tuple(v.split('=')) for v in rmisc])
        return CONLLUPToken(*line[:9], misc, *line[10:13], rmisc)


class CONLLUToken(namedtuple('CONLLUToken', ['index', 'form', 'lemma', 'upos', 'msd', 'upos_feats', 'head', 'deprel',
                                             'deps', 'misc'])):
    def to_conllu_line(self):
        out = '{}\t'.format('\t'.join(self[:9]))
        misc = ['{}={}'.format(k, v) for k, v in self.misc.items()]
        out += '{}\n'.format('|'.join(misc) or '_')
        return out

    @staticmethod
    def create_from_conllup_token(token, transfers=[]):
        if 'NE' in transfers and token.ne not in CORPUS_NULL_VALUES:
            token.misc.update({'NER': token.ne})

        if 'DP' in transfers and token.dp not in CORPUS_NULL_VALUES:
            token.misc.update({'DP': token.dp})

        if 'SRL' in transfers and token.srl not in CORPUS_NULL_VALUES:
            token.misc.update({'SRL': token.srl})

        if 'RMISC' in transfers:
            token.misc.update(token.rmisc)

        return CONLLUToken(*token[:10])


def generate(input_stream, output_stream, datasets=[], annotations=[], misc=[], keep_status=False):

    flush = False
    read_buffer = StringIO()

    for line in input_stream:
        if line.startswith('# global.columns') or (flush and not line.startswith('# newdoc')):
            continue

        if line.startswith('# newdoc'):
            flush = False
            read_buffer = StringIO()
            if datasets or annotations:
                read_buffer.write(line)
            else:
                output_stream.write(line)

        elif line.startswith('# contained_in_datasets'):
            if datasets:
                datasets = DATASETS_RE.search(line).group(0).split(';')
                if not set(datasets).intersection(datasets):
                    flush = True
                    continue
                if annotations:
                    if keep_status:
                        read_buffer.write(line)
                else:
                    output_stream.write(read_buffer.getvalue())
                    read_buffer = StringIO()
                    if keep_status:
                        output_stream.write(line)
            else:
                output_stream.write(read_buffer.getvalue())
                read_buffer = StringIO()
                if keep_status:
                    output_stream.write(line)

        elif line.startswith('# annotation_levels'):
            if annotations:
                annotations = ANNOTATIONS_RE.search(line).group(0).split(';')
                if not all([a in annotations for a in annotations]):
                    flush = True
                    continue
                output_stream.write(read_buffer.getvalue())
                read_buffer = StringIO()
                if keep_status:
                    output_stream.write(line)
            else:
                output_stream.write(read_buffer.getvalue())
                read_buffer = StringIO()
                if keep_status:
                    output_stream.write(line)

        elif line.startswith('# ') or not line.strip():
            output_stream.write(line)

        else:
            output_stream.write(
                CONLLUToken.create_from_conllup_token(
                    CONLLUPToken.create_from_conllup_line(line.strip()),
                    misc
                ).to_conllu_line()
            )


def main(args):
    output_file = args.output_file or '{}.conllu'.format(os.path.splitext(args.source)[0])
    datasets = set(args.datasets)
    annotations = set(args.annotations)

    with open(args.source, 'r') as infile, open(output_file, 'w') as outfile:
        generate(infile, outfile, datasets, annotations, args.misc, args.keep_status)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='CONLLU corpus generator',
        description='Generates corpus in .conllu format from .conllup source',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('source', help='Path to the source file.')
    parser.add_argument('-o', dest='output_file', help='Path to the output file.')
    parser.add_argument('-d', '--datasets', type=str, nargs='*', default=[],
                        help='Filter documents by containment in datasets.')
    parser.add_argument('-a', '--annotations', type=str, nargs='*', default=[],
                        help='Filter documents by level of annotation.')
    parser.add_argument('-m', '--misc', type=str, nargs='*', default=[],
                        help='Transfer data from these columns to MISC.')
    parser.add_argument('--keep-status-metadata', dest='keep_status', action='store_true',
                        help='Write document status metadata to output file.')
    args = parser.parse_args()
    main(args)
