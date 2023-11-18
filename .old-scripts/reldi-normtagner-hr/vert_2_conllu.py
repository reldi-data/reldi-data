import re
from collections import namedtuple


class Multitoken(namedtuple('Multitoken', ['multitoken', 'tokens', 'misc'])):
    def append_misc(self, misc):
        self.misc.append(misc)

    def to_conllu_line(self, index):
        out = '{}\t{}\t{}\t{}\n'.format(
            '{}-{}'.format(str(index), str(index+len(self.tokens)-1)),
            self.multitoken,
            '\t'.join(7*['_']),
            '|'.join(self[-1]) or '_'
        )
        for token in self.tokens:
            out += token.to_conllu_line(index)
            index += 1
        return out


class Token(namedtuple('Token', ['form', 'lemma', 'upos', 'msd', 'upos_feats', 'head', 'deprel', 'deps', 'misc'])):
    def to_conllu_line(self, index):
        out = '{}\t{}\t'.format(index, '\t'.join(self[:5]))
        head = self.head
        try:
            if int(self.head) < 0:
                head = str(index+int(self.head))
        except:
            pass
        out += '{}\t'.format(head)
        out += '{}\t{}\n'.format('\t'.join(self[6:-1]), '|'.join(self[-1]) or '_')
        return out

    def append_misc(self, misc):
        self.misc.append(misc)

    @staticmethod
    def create_from_vert_line(line, ner, ner_first):
        form, norm, lemma, msd, _, upos, upos_feats, _ = line.split('\t')
        if ' ' in norm:
            tokens = []
            multitoken = form
            forms = norm.split(' ')
            lemmata = [l.rsplit('-', 1)[0] for l in lemma.split(' ')]
            upos = upos.split(' ')
            msds = msd.split(' ')
            upos_feats = upos_feats.split(' ')
            is_true_multitoken = multitoken != norm.replace(' ', '')
            multitoken_size = len(forms)
            for i, (f, l, p, m, s) in enumerate(zip(forms, lemmata, upos, msds, upos_feats), start=1):
                if p == '_':
                    p = UPOS_MAPPER[m]
                misc = []
                if not is_true_multitoken and i < multitoken_size:
                    misc.extend(['SpaceAfter=No', 'CorrectSpaceAfter=Yes'])
                if ner is not None:
                    if ner_first:
                        misc.append('NER=B-'+ner)
                        ner_first = False
                    else:
                        misc.append('NER=I-'+ner)

                tokens.append(Token(f, l, p, m, s, '_', '_', '_', misc))
            if is_true_multitoken:
                return [Multitoken(multitoken, tokens, [])]
            else:
                return tokens
        elif ' ' in form:
            tokens = []
            forms = form.split(' ')
            lemma = lemma.rsplit('-', 1)[0]
            if upos == '_':
                upos = UPOS_MAPPER[msd]
            for i, form in enumerate(forms, start=1):
                misc = []
                if ner is not None:
                    if ner_first:
                        misc.append('NER=B-'+ner)
                        ner_first = False
                    else:
                        misc.append('NER=I-'+ner)

                if i == 1:
                    misc.append('Normalized={}'.format(norm))
                    tokens.append(Token(form, lemma, upos, msd, upos_feats, '_', '_', '_', misc))
                else:
                    tokens.append(Token(form, '_', 'X', '_', '_', -1, 'goeswith', '_', misc))
            return tokens
        else:
            if upos == '_':
                upos = UPOS_MAPPER[msd]
            misc = []
            if form != norm:
                misc.append('Normalized={}'.format(norm))
            if ner is not None:
                if ner_first:
                    misc.append('NER=B-'+ner)
                else:
                    misc.append('NER=I-'+ner)
            return [Token(form, lemma.rsplit('-', 1)[0], upos, msd, upos_feats, '_', '_', '_', misc)]


attrs = re.compile(r'id="tid\.(.+?)" .+? type="tweet" std_tech="(.+?)" std_ling="(.+?)">')
type_re = re.compile(r'type="(.+?)"')
ner = None
UPOS_MAPPER = {'Xa': 'SYM', 'Xh': 'SYM', 'Xe': 'SYM', 'Xf': 'X', 'X': 'X', 'Xw': 'SYM'}

with open('reldi-normtagner-hr.conllu', 'w') as out:
    for line in open('reldi-normtagner-hr.vert'):
        if line.startswith('<text'):
            tweet_id, t, l = attrs.search(line).groups()
            out.write("# newdoc id = {}\n".format(tweet_id))
            out.write("# T = {}\n".format(t[-1]))
            out.write("# L = {}\n".format(l[-1]))
            sid = 0
        elif line.startswith('<s>'):
            sid += 1
            tid = 0
            out.write('# sent_id = {}.{}\n'.format(tweet_id, sid))
            sent = []
        elif line.startswith('<name '):
            ner = type_re.search(line).group(1)
            first = True
        elif line.startswith('</name>'):
            ner = None
        elif line.startswith('<g/>'):
            sent[-1].append_misc('SpaceAfter=No')
        elif line.startswith('</s>'):
            text = ''
            for token in sent:
                text += token[0]
                if 'SpaceAfter=No' not in token[-1]:
                    text += ' '
            out.write('# text = {}\n'.format(text.strip()))
            tid = 1
            for token in sent:
                out.write(token.to_conllu_line(tid))
                if isinstance(token, Multitoken):
                    tid += len(token.tokens)
                else:
                    tid += 1
            out.write('\n')
        elif '\t' in line:
            token, norm, lemma, msd, msd_feats, upos, upos_feats, normed = line.split('\t')
            sent.extend(Token.create_from_vert_line(line, ner, first))
            if ner is not None and first:
                first = False
