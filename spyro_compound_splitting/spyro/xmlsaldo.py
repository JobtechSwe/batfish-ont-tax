# encoding: utf-8

import os
from xml.etree import cElementTree as ElementTree
from saldo import DB_PATH


class XMLSALDO:
    def __init__(self, saldo_path, morph_path):
        """Load SALDO and its morphology lexicon to memory.

        saldo_path -- path to saldo.xml from Sprakbanken
        morph_path -- path to saldom.xml from Sprakbanken
        """

        # map of sense identifiers (e.g. upphäva..1) to tuples:
        #   (list of sense identifiers for primary descriptors,
        #    list of sense identifiers for secondary descriptors,
        #    list of lemgram identifiers)
        self.senses = {}

        # map of lemgram identifiers (e.g. opphäva..vb.2) to tuples:
        #   (citation form, part of speech, paradigm identifier,
        #    list of (form string, morphology description) tuples,
        #    list of sense identifiers)
        #
        self.lemgrams = {}

        print "Loading SALDO"
        self._read_saldo(saldo_path)
        print "Loading SALDO morphology"
        self._read_morph(morph_path)
        print "Cross-linking"
        self._cross_link()
        print "Done"

    def _read_saldo(self, path):
        etree = ElementTree.parse(open(path, 'rb'))
        for el_entry in etree.getiterator('LexicalEntry'):
            el_lemma = el_entry.find('Lemma')
            lemgrams = []
            for el_form in el_lemma.getiterator('FormRepresentation'):
                lemgram = None
                for el_feat in el_form.getiterator('feat'):
                    att = el_feat.get('att')
                    val = el_feat.get('val')
                    if att == 'lemgram':
                        lemgram = val
                        break
                assert not lemgram is None
                lemgrams.append(lemgram)
            el_sense = el_entry.find('Sense')
            assert not el_sense is None
            sense_id = el_sense.get('id')
            assert not sense_id is None
            primary = []
            secondary = []
            for el_relation in el_sense.getiterator('SenseRelation'):
                targets = el_relation.get('targets')
                assert not targets is None
                for el_feat in el_relation.getiterator('feat'):
                    att = el_feat.get('att')
                    val = el_feat.get('val')
                    if att == 'label':
                        if val == 'primary': primary.append(targets)
                        elif val == 'secondary': secondary.append(targets)
            if sense_id == 'PRIM..1':
                assert len(primary) == 0
                primary.append('PRIM..1')
            if len(primary) != 1: print sense_id
            assert len(primary) == 1
            self.senses[sense_id] = (primary, secondary, lemgrams)

    def _read_morph(self, path):
        etree = ElementTree.parse(open(path, 'rb'))
        for el_entry in etree.getiterator('LexicalEntry'):
            gf, lemgram, pos, paradigm = (None,)*4
            el_lemma = el_entry.find('Lemma')
            for el_form in el_lemma.getiterator('FormRepresentation'):
                for el_feat in el_form.getiterator('feat'):
                    att = el_feat.get('att')
                    val = el_feat.get('val')
                    if att == 'writtenForm':    gf = val
                    elif att == 'lemgram':      lemgram = val
                    elif att == 'partOfSpeech': pos = val
                    elif att == 'paradigm':     paradigm = val
            assert not gf is None
            assert not lemgram is None
            assert not pos is None
            assert not paradigm is None
            forms = []
            for el_wordform in el_entry.getiterator('WordForm'):
                form, msd = None, None
                for el_feat in el_wordform.getiterator('feat'):
                    att = el_feat.get('att')
                    val = el_feat.get('val')
                    if att == 'writtenForm':    form = val
                    elif att == 'msd':          msd = val
                assert not form is None
                assert not msd is None
                forms.append((form, msd))

            self.lemgrams[lemgram] = (gf, pos, paradigm, forms, [])

    def _cross_link(self):
        keep_senses = set()
        for sense_id, (_, _, lemgram_ids) in self.senses.iteritems():
            for lemgram_id in lemgram_ids:
                lemgram = self.lemgrams.get(lemgram_id)
                if not lemgram is None:
                    lemgram[4].append(sense_id)
                    keep_senses.add(sense_id)
                else:
                    print (u"Warning: lemgram %s does not exist" %
                        lemgram_id).encode('utf-8')
        for sense_id in self.senses.keys():
            if not sense_id in keep_senses: del self.senses[sense_id]

    def write_sqlite(self, conn):
        c = conn.cursor()
        c.execute(
"CREATE TABLE senses (sense TEXT, mother TEXT)")
        c.execute(
"CREATE TABLE senses_lemgrams (sense_id INT, lemgram_id INT)")
        c.execute(
"CREATE TABLE senses_secondary (sense_id INT, father TEXT)")
        c.execute(
"CREATE TABLE lemgrams (lemgram TEXT, gf TEXT, pos TEXT, paradigm TEXT)")
        c.execute(
"CREATE TABLE lemgrams_forms (lemgram_id INT, form TEXT, msd TEXT)")

        sense_id_rowid = {}
        for sense_id,(primary,secondary,lemgrams) in self.senses.iteritems():
            c.execute("INSERT INTO senses (sense, mother) VALUES (?,?)", 
                (sense_id, primary[0]))
            sense_rowid = c.lastrowid
            for s in secondary:
                c.execute(
"INSERT INTO senses_secondary (sense_id, father) VALUES (?,?)", (
                    sense_rowid, s))
            sense_id_rowid[sense_id] = sense_rowid

        for lemgram_id, (gf,pos,paradigm,forms,senses) in \
        self.lemgrams.iteritems():
            c.execute(
"INSERT INTO lemgrams (lemgram, gf, pos, paradigm) VALUES (?,?,?,?)", (
                lemgram_id, gf, pos, paradigm))
            lemgram_rowid = c.lastrowid
            for sense_id in senses:
                sense_rowid = sense_id_rowid[sense_id]
                c.execute(
"INSERT INTO senses_lemgrams (sense_id, lemgram_id) VALUES (?,?)",
                    (sense_rowid, lemgram_rowid))
            for form, msd in forms:
                c.execute(
"INSERT INTO lemgrams_forms (lemgram_id, form, msd) VALUES (?,?,?)",
                    (lemgram_rowid, form, msd))

        conn.commit()

        c.execute("CREATE INDEX idx_senses_sense ON senses (sense)")
        c.execute("CREATE INDEX idx_senses_primary ON senses (mother)")
        c.execute(
"CREATE INDEX idx_senses_secondary_id ON senses_secondary (sense_id)")
        c.execute(
"CREATE INDEX idx_senses_secondary ON senses_secondary (father)")
        c.execute(
"CREATE INDEX idx_senses_lemgrams_sense ON senses_lemgrams (sense_id)")
        c.execute(
"CREATE INDEX idx_senses_lemgrams_lemgram ON senses_lemgrams (lemgram_id)")
        c.execute("CREATE INDEX idx_lemgrams_lemgram ON lemgrams (lemgram)")
        c.execute(
"CREATE INDEX idx_lemgrams_forms_lemgram ON lemgrams_forms (lemgram_id)")
        c.execute(
"CREATE INDEX idx_lemgrams_forms_form ON lemgrams_forms (form)")
        c.execute(
"CREATE INDEX idx_lemgrams_gf ON lemgrams (gf)")

        conn.commit()

if __name__ == '__main__':
    import sys, sqlite3
    assert sys.argv[1].endswith('.xml')
    assert sys.argv[2].endswith('.xml')
    try: os.remove(DB_PATH)
    except OSError: pass
    conn = sqlite3.connect(DB_PATH)
    saldo = XMLSALDO(sys.argv[1], sys.argv[2])
    saldo.write_sqlite(conn)

