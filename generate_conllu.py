import argparse
import os
import re

from collections import namedtuple, OrderedDict
from enum import Enum
from io import StringIO


DATASETS_RE = re.compile(r'(?<=(?:# contained_in_datasets = ))(.+)(?=\n)')
ANNOTATIONS_RE = re.compile(r'(?<=(?:# annotation_levels = ))(.+)(?=\n)')

CORPUS_NULL_VALUES = ['_', '*']
ReadingMode = Enum('ReadingMode', ['DOCUMENT', 'SENTENCE'])


class InvalidCONLLUPToken(TypeError):
    pass


class CONLLUPToken(namedtuple('CONLLUPToken', ['index', 'form', 'lemma', 'upos', 'msd', 'upos_feats', 'head', 'deprel',
                                               'deps', 'misc', 'ne', 'dp', 'srl', 'parseme_mwe', 'rmisc'])):
    @staticmethod
    def create_from_conllup_line(line):
        line = line.split('\t')

        if len(line) != 15:
            raise InvalidCONLLUPToken("Invalid token. Expected 15 columns, got {}.".format(str(len(line))))

        if line[9] == '_':
            misc = []
        else:
            misc = line[9].split('|')
        misc = OrderedDict([tuple(v.split('=')) for v in misc])
        if line[14] == '_':
            rmisc = []
        else:
            rmisc = line[14].split('|')
        rmisc = OrderedDict([tuple(v.split('=')) for v in rmisc])
        return CONLLUPToken(*line[:9], misc, *line[10:14], rmisc)


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

        if 'PARSEME' in transfers and token.parseme_mwe not in CORPUS_NULL_VALUES:
            token.misc.update({'PARSEME': token.parseme_mwe})

        if 'RMISC' in transfers:
            token.misc.update(token.rmisc)

        return CONLLUToken(*token[:10])


def generate(input_stream, output_stream, datasets=[], omit_datasets=[], annotations=[], omit_annotations=[],
             misc=[], keep_status=False):

    line_no = 0

    def consume_till_end(*end_marks, flush=False):
        nonlocal line_no

        while True:
            line = input_stream.readline()
            line_no += 1

            if not line or any([line.startswith(end_mark) for end_mark in end_marks]):
                break

            if flush:
                continue

            if line.startswith('# contained_in_datasets') or line.startswith('# annotation_levels'):
                if keep_status:
                    output_stream.write(line)

            elif line.startswith('# ') or not line.strip():
                output_stream.write(line)

            else:
                try:
                    output_stream.write(
                        CONLLUToken.create_from_conllup_token(
                            CONLLUPToken.create_from_conllup_line(line.strip()),
                            misc
                        ).to_conllu_line()
                    )
                except InvalidCONLLUPToken as e:
                    raise TypeError('Line number {}: {}'.format(line_no, str(e)))

        return line

    read_buffer = StringIO()

    reading_mode = ReadingMode.DOCUMENT

    line = input_stream.readline()
    line_no += 1

    while True:

        if not line:
            break

        if line.startswith('# global.columns'):
            line = input_stream.readline()
            line_no += 1
            continue

        if line.startswith('# newdoc'):
            reading_mode = ReadingMode.DOCUMENT
            read_buffer = StringIO()
            if any([datasets, omit_datasets, annotations, omit_annotations]):
                # there are limitations, buffer and wait
                read_buffer.write(line)
            else:
                # no limitations, write till the end
                output_stream.write(line)
                line = consume_till_end('# newdoc')
                continue

        elif line.startswith('# sent_id'):
            read_buffer = StringIO()
            if reading_mode == ReadingMode.SENTENCE and any([datasets, omit_datasets]):
                # there are limitations, buffer and wait
                read_buffer.write(line)
            else:
                # no limitations, write till the end
                line = consume_till_end('# sent_id', '# newdoc')
                continue

        elif line.startswith('# contained_in_datasets'):
            if reading_mode == ReadingMode.DOCUMENT:
                if datasets or omit_datasets:
                    # there are dataset-related limitations
                    doc_datasets = DATASETS_RE.search(line).group(0).split(';')
                    if omit_datasets and set([d.strip('*') for d in doc_datasets]).intersection(omit_datasets):
                        # document is part of the omited dataset(s), reset buffer and flush
                        read_buffer = StringIO()
                        line = consume_till_end('# newdoc', flush=True)
                        continue
                    if datasets and not set([d.strip('*') for d in doc_datasets]).intersection(datasets):
                        # document is not part of the required dataset(s), reset buffer and flush
                        read_buffer = StringIO()
                        line = consume_till_end('# newdoc', flush=True)
                        continue

                    if datasets and any([d.endswith('*') for d in doc_datasets]):
                        # document is partially in different datasets, switch to sentence mode
                        reading_mode = ReadingMode.SENTENCE

                    if annotations or omit_annotations:
                        # there are annotations-related limitations, buffer and wait
                        if keep_status:
                            read_buffer.write(line)
                    else:
                        # there are no annotations-related limitations, output buffered content and reset buffer
                        output_stream.write(read_buffer.getvalue())
                        read_buffer = StringIO()
                        if keep_status:
                            output_stream.write(line)

                        if reading_mode == ReadingMode.DOCUMENT:
                            # no limitations and in document mode, write till the end
                            line = consume_till_end('# newdoc')
                            continue

                elif annotations or omit_annotations:
                    # there are annotations-related limitations, buffer and wait
                    if keep_status:
                        read_buffer.write(line)
                else:
                    # there are no limitations, output buffered content and reset buffer
                    output_stream.write(read_buffer.getvalue())
                    read_buffer = StringIO()
                    if keep_status:
                        output_stream.write(line)

                    if reading_mode == ReadingMode.DOCUMENT:
                        # no limitations and in document mode, write till the end
                        line = consume_till_end('# newdoc')
                        continue

            elif reading_mode == ReadingMode.SENTENCE:
                if datasets or omit_datasets:
                    # there are dataset-related limitations
                    doc_datasets = DATASETS_RE.search(line).group(0).split(';')
                    if omit_datasets and set(doc_datasets).intersection(omit_datasets):
                        # sentence is part of the omited dataset(s), reset buffer and flush
                        line = consume_till_end('# sent_id', '# newdoc', flush=True)
                        continue
                    if datasets and not set(doc_datasets).intersection(datasets):
                        # sentence is not part of the required dataset(s), reset buffer and flush
                        line = consume_till_end('# sent_id', '# newdoc', flush=True)
                        continue

                # pass all limitations, output buffered content and reset buffer
                output_stream.write(read_buffer.getvalue())
                read_buffer = StringIO()
                if keep_status:
                    output_stream.write(line)

                # write till the end
                line = consume_till_end('# sent_id', '# newdoc')
                continue

        elif line.startswith('# annotation_levels'):
            if annotations or omit_annotations:
                # there are annotations-related limitations
                doc_annotations = ANNOTATIONS_RE.search(line).group(0).split(';')
                if omit_annotations and any([a in doc_annotations for a in omit_annotations]):
                    # document contains omited annotation(s), reset buffer and flush
                    read_buffer = StringIO()
                    line = consume_till_end('# newdoc', flush=True)
                    continue
                if annotations and not all([a in doc_annotations for a in annotations]):
                    # document has no required annotation(s), reset buffer and flush
                    read_buffer = StringIO()
                    line = consume_till_end('# newdoc', flush=True)
                    continue

            # pass all limitations, output buffered content and reset buffer
            output_stream.write(read_buffer.getvalue())
            read_buffer = StringIO()
            if keep_status:
                output_stream.write(line)

            if reading_mode == ReadingMode.DOCUMENT:
                # in document mode, write till the end
                line = consume_till_end('# newdoc')
                continue

        elif line.startswith('# ') or not line.strip():
            output_stream.write(line)

        else:
            # shouldn't end up here
            try:
                output_stream.write(
                    CONLLUToken.create_from_conllup_token(
                        CONLLUPToken.create_from_conllup_line(line.strip()),
                        misc
                    ).to_conllu_line()
                )
            except InvalidCONLLUPToken as e:
                raise TypeError('Line number {}: {}'.format(line_no, str(e)))

        line = input_stream.readline()
        line_no += 1


def main(args):
    output_file = args.output_file or '{}.conllu'.format(os.path.splitext(args.source)[0])
    datasets = set(args.datasets)
    omit_datasets = set(args.omit_datasets)
    annotations = set(args.annotations)
    omit_annotations = set(args.omit_annotations)

    with open(args.source, 'r') as infile, open(output_file, 'w') as outfile:
        generate(infile, outfile, datasets, omit_datasets, annotations, omit_annotations, args.misc, args.keep_status)


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
    parser.add_argument('-t', '--omit-datasets', type=str, nargs='*', default=[],
                        help='Filter documents by not being contained in datasets.')
    parser.add_argument('-a', '--annotations', type=str, nargs='*', default=[],
                        help='Filter documents by level of annotation.')
    parser.add_argument('-n', '--omit-annotations', type=str, nargs='*', default=[],
                        help='Filter documents by not having certain level of annotation.')
    parser.add_argument('-m', '--misc', type=str, nargs='*', default=[],
                        choices=['NE', 'DP', 'SRL', 'PARSEME', 'RMISC'],
                        help='Transfer data from these columns to MISC.')
    parser.add_argument('--keep-status-metadata', dest='keep_status', action='store_true',
                        help='Write document status metadata to output file.')
    args = parser.parse_args()
    main(args)
