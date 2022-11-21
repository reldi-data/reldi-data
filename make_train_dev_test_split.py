import argparse
import os
import re
import uuid

from conll_corpus_splitter.conll_corpus_splitter import CONLLCorpusIterator, split_corpus, COMMENT_PATTERN
from conll_corpus_splitter.conll_corpus_splitter.utils import MetadataDiffDict
from contextlib import ExitStack
from generate_conllu import generate


class CONLLCorpusDocumentIterator(CONLLCorpusIterator):
    def __init__(self, *filenames, sample_start_pattern=r'^#\snewdoc\sid\s?=',
                 comment_pattern=COMMENT_PATTERN, ignore_metadata_attributes=['global.columns']):
        super().__init__(*filenames, sample_start_pattern=sample_start_pattern, sample_end_pattern=sample_start_pattern,
                         comment_pattern=comment_pattern, ignore_metadata_attributes=ignore_metadata_attributes,
                         append_newline=False)

    def __iter__(self):
        with ExitStack() as stack:
            files = [stack.enter_context(open(filename, 'r')) for filename in self.filenames]
            line_index = -1
            for file in files:
                text_buffer = ''
                metadata = MetadataDiffDict()
                reading_sample = False
                for line in file:
                    line_index += 1
                    if re.match(self.sample_start_pattern, line) and reading_sample:
                        # end of sample
                        yield text_buffer, metadata.copy()
                        reading_sample = True
                        text_buffer = line
                        metadata = MetadataDiffDict()
                    elif re.match(self.sample_start_pattern, line):
                        # start of sample
                        reading_sample = True
                        text_buffer += line
                        metadata = MetadataDiffDict()
                    elif reading_sample:
                        text_buffer += line


def main(args):
    intermediate_filename = str(uuid.uuid4().hex)
    if args.keep_conllu:
        intermediate_filename = '{}.conllu'.format(os.path.splitext(args.source)[0])

    annotations = set(args.annotations)

    with open(args.source, 'r') as infile, open(intermediate_filename, 'w') as outfile:
        generate(infile, outfile, annotations=annotations, misc=args.misc, keep_status=args.keep_status)

    output_folder = args.output_folder or os.getcwd()
    split_corpus(intermediate_filename, output_folder=output_folder, test=args.test, dev=args.dev,
                 seed=args.seed, cross_validation=args.cross_validation, omit_metadata=True,
                 output_filename=args.output_filename, iterator_cls=CONLLCorpusDocumentIterator)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='CONLLUP corpus splitter',
        description='Generates .conllu corpus from .conllup source and splits it reproducibly into train, '
                    'dev and test set.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    io_group = parser.add_argument_group("Input / output options")
    io_group.add_argument('source', help='Path to the source .conllup file.')
    io_group.add_argument('-o', dest='output_folder', help='Path to the output folder.')
    io_group.add_argument('-f', '--output-filename', dest='output_filename', type=str,
                          help='Specify the filename for output files.')
    io_group.add_argument('--keep-conllu', dest='keep_conllu', action='store_false',
                          help='Keep intermediate .conllu file.')

    generate_group = parser.add_argument_group(".conllu generation options")
    generate_group.add_argument('-a', '--annotations', type=str, nargs='*', default=[],
                                help='Filter documents by level of annotation.')
    generate_group.add_argument('-m', '--misc', type=str, nargs='*', default=[],
                                help='Transfer data from these columns to MISC.')
    generate_group.add_argument('--keep-status-metadata', dest='keep_status', action='store_true',
                                help='Write document status metadata to output file.')

    split_group = parser.add_argument_group("Split options")
    split_group.add_argument('-t', '--test', type=float, help='Test set size.', default=0.3)
    split_group.add_argument('-d', '--dev', type=float, help='Dev set size.', default=0.0)
    split_group.add_argument('-s', '--seed', type=int, help='Manually set random seed.')
    split_group.add_argument('--cross-validation', dest='cross_validation', action='store_true',
                             help='Create k-fold cross-validation datasets.')
    args = parser.parse_args()
    main(args)
