import argparse
import os

from msd_mapper import MSDMapper
from generate_conllu import CONLLUPToken

mapper = MSDMapper()


def main(args):
    output_filename = args.output_file
    if not output_filename:
        output_filename = '{}.uposxpos.txt'.format(os.path.splitext(args.source)[0])

    with open(output_filename, 'w') as f:
        for line in open(args.source, 'r'):
            if line.startswith('#') or line.startswith('\n') or '-' in line.split('\t')[0]:
                f.write(line)
                continue
            token = CONLLUPToken(*line.strip().split('\t'))
            mtefeat, upos, udfeat = mapper.map_word(token.form, token.lemma, token.msd)
            if token.upos == upos and token.upos_feats == udfeat:
                f.write(line)
                continue
            upos_tag = '{}|{}'.format(token.upos, token.upos_feats)
            if upos_tag not in mapper.uposudfeat_msd:
                print('UPOS', token.msd, 'UposTag={}'.format(upos_tag))
                f.write('UPOS!!!\t'+line)
            elif token.msd not in mapper.uposudfeat_msd[upos_tag]:
                    print('XPOS', token.msd, upos_tag)
                    f.write('XPOS!!!\t'+line)
            else:
                print('LAST RESORT')
                f.write(line)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        prog='CONLLUP tag mapping validator',
        description='Validates mapping of XPOS to UPOS tags in a CONLLUP corpus.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument('source', help='Path to the source file.')
    parser.add_argument('-o', '--output', dest='output_file', help='Path to the output file.')
    args = parser.parse_args()
    main(args)
