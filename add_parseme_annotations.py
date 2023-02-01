import argparse
import json
import re

from collections import namedtuple


SENTENCE_ID_RE = re.compile(r'(?<=(?:# sent_id = ))(.+)(?=\n)')


class InvalidCONLLUPToken(TypeError):
    pass


class CONLLUPToken(namedtuple('CONLLUPToken', ['index', 'form', 'lemma', 'upos', 'msd', 'upos_feats', 'head', 'deprel',
                                               'deps', 'misc', 'ne', 'dp', 'srl', 'parseme_mwe', 'rmisc'])):
    @staticmethod
    def create_from_conllup_line(line):
        line = line.split('\t')

        if len(line) != 15:
            raise InvalidCONLLUPToken("Invalid token. Expected 15 columns, got {}.".format(str(len(line))))

        return CONLLUPToken(*line)

    @staticmethod
    def create_from_conllup_token(token, parseme_mwe):
        return CONLLUPToken(*token[:13], parseme_mwe, token[14])

    def to_conllup_line(self):
        return '{}\n'.format('\t'.join(self))


def add_annotations(input_stream, output_stream, annotation_data):

    current_sentence_id = None
    sentence = []

    for line in input_stream:
        if line.startswith('# sent_id'):
            current_sentence_id = SENTENCE_ID_RE.search(line).group(0)
            output_stream.write(line)

        elif line.startswith('# '):
            output_stream.write(line)

        elif not line.strip():
            if current_sentence_id in annotation_data:
                current_sentence_annotations = {a[0]: a[2] for a in annotation_data[current_sentence_id]['annotations']}
                for i in range(len(sentence)):
                    sentence[i] = CONLLUPToken.create_from_conllup_token(
                        sentence[i],
                        current_sentence_annotations.get(sentence[i].index, '*')
                    )
            for token in sentence:
                output_stream.write(token.to_conllup_line())
            current_sentence_id = None
            sentence = []
            output_stream.write(line)

        else:
            sentence.append(CONLLUPToken.create_from_conllup_line(line.strip()))


def main(args):
    annotation_data = json.loads(open(args.annotation_data, 'r').read())
    with open(args.source, 'r') as infile, open(args.output_file, 'w') as outfile:
        add_annotations(infile, outfile, annotation_data)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='PARSEME:MWE to CONLLUP file',
        description='Adds PARSEME:MWE annotations to CONLLUP file',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('source', help='Path to the source file.')
    parser.add_argument('annotation_data', help='Path to the annotation data .json file.')
    parser.add_argument('-o', dest='output_file', help='Path to the output file.')
    args = parser.parse_args()
    main(args)
