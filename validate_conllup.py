import argparse

from generate_conllu import generate
from io import StringIO
import subprocess


def main(args):
    outfile = StringIO()

    with open(args.input, 'r') as infile:
        generate(infile, outfile)

    outfile.seek(0)

    proc_args = ["python3", "ud-tools/validate.py"]

    if args.quiet:
        proc_args.extend(["--quiet"])

    if args.max_err:
        proc_args.extend(["--max-err", str(args.max_err)])

    if args.lang:
        proc_args.extend(["--lang", args.lang])

    if args.level:
        proc_args.extend(["--level", str(args.level)])

    if not args.single_root:
        proc_args.extend(["--multiple-roots"])

    if not args.check_tree_text:
        proc_args.extend(["--no-tree-text"])

    if not args.check_space_after:
        proc_args.extend(["--no-space-after"])

    if args.check_coref:
        proc_args.extend(["--coref"])

    proc = subprocess.Popen(proc_args, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    outs, errs = proc.communicate(input=outfile.read().encode(), timeout=90)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='CONLLUP corpus validator',
        description='Validates corpus in .conllup',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    io_group = parser.add_argument_group("Input / output options")
    io_group.add_argument('--quiet', dest="quiet", action="store_true", default=False, help='Do not print any error messages. Exit with 0 on pass, non-zero on fail.')
    io_group.add_argument('--max-err', action="store", type=int, default=20, help='How many errors to output before exiting? 0 for all. Default: %(default)d.')
    io_group.add_argument('input', help='Path to the source .conllup file.')

    list_group = parser.add_argument_group("Tag sets", "Options relevant to checking tag sets.")
    list_group.add_argument("--lang", action="store", required=True, default=None, help="Which langauge are we checking? If you specify this (as a two-letter code), the tags will be checked using the language-specific files in the data/ directory of the validator.")
    list_group.add_argument("--level", action="store", type=int, default=5, dest="level", help="Level 1: Test only CoNLL-U backbone. Level 2: UD format. Level 3: UD contents. Level 4: Language-specific labels. Level 5: Language-specific contents.")

    tree_group = parser.add_argument_group("Tree constraints", "Options for checking the validity of the tree.")
    tree_group.add_argument("--multiple-roots", action="store_false", default=True, dest="single_root", help="Allow trees with several root words (single root required by default).")

    meta_group = parser.add_argument_group("Metadata constraints", "Options for checking the validity of tree metadata.")
    meta_group.add_argument("--no-tree-text", action="store_false", default=True, dest="check_tree_text", help="Do not test tree text. For internal use only, this test is required and on by default.")
    meta_group.add_argument("--no-space-after", action="store_false", default=True, dest="check_space_after", help="Do not test presence of SpaceAfter=No.")

    coref_group = parser.add_argument_group("Coreference / entity constraints", "Options for checking coreference and entity annotation.")
    coref_group.add_argument('--coref', action='store_true', default=False, dest='check_coref', help='Test coreference and entity-related annotation in MISC.')
    args = parser.parse_args()
    main(args)
