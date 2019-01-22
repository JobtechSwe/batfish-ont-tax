import sqlite3
import os


DATA_PATH = os.path.join(
    os.environ['HOME'], 'Utveckling', 'JobtechSwe', 'batfish-ont-tax', 'spyro_compound_splitting', 'spyro')
DB_PATH = os.path.join(DATA_PATH, 'saldo.sqlite')


def _get_cached(cache, x, f):
    y = cache.get(x)
    if y is None:
        y = f(x)
        cache[x] = y
    return y


class SALDO:
    def __init__(self, sqlite_path=DB_PATH):
        assert os.path.exists(sqlite_path)
        self.conn = sqlite3.connect(sqlite_path)
        self.senses_cache = {}
        self.lemgrams_cache = {}
        self.lemgram_forms_cache = {}
        self.lemgram_senses_cache = {}
        self.form_lemgrams_cache = {}
        self.gf_lemgrams_cache = {}

    def db_get_lemgram(self, lemgram):
        lemgrams = tuple(self.conn.execute(
            "SELECT lemgram, gf, pos, paradigm FROM lemgrams WHERE lemgram = ?",
            (lemgram,)))
        assert len(lemgrams) <= 1
        if len(lemgrams) == 0:
            return None
        return lemgrams[0]

    def db_get_lemgrams_by_form(self, form):
        return tuple(self.conn.execute(
            """SELECT DISTINCT lemgram, gf, pos, paradigm FROM lemgrams, lemgrams_forms
            WHERE lemgram_id = lemgrams.rowid AND form = ?""", (form,)))
    
    def db_get_lemgrams_by_gf(self, gf):
        return tuple(self.conn.execute(
            "SELECT DISTINCT lemgram, gf, pos, paradigm FROM lemgrams WHERE gf = ?",
            (gf,)))

    def db_get_lemgrams_pos_msd_by_form(self, form):
        return tuple(self.conn.execute(
            """SELECT lemgram, pos, msd FROM lemgrams, lemgrams_forms
            WHERE lemgram_id = lemgrams.rowid AND form = ?""", (form,)))

    def db_get_forms_by_lemgram(self, lemgram):
        return tuple(self.conn.execute(
            """SELECT form, msd FROM lemgrams, lemgrams_forms
            WHERE lemgram_id = lemgrams.rowid AND lemgram = ?""", (lemgram,)))

    def db_get_sense(self, sense):
        senses = list(self.conn.execute(
            "SELECT rowid, sense, mother FROM senses WHERE sense = ?", (sense,)))
        assert len(senses) <= 1
        if len(senses) == 0:
            return None
        sense_rowid, sense, primary = senses[0]
        secondary = [secondary for secondary, in self.conn.execute(
            "SELECT father FROM senses_secondary WHERE sense_id = ?", (sense_rowid,))]
        lemgrams = [lemgram for lemgram, in self.conn.execute(
            """SELECT lemgram FROM senses_lemgrams,lemgrams WHERE
            lemgrams.rowid = senses_lemgrams.lemgram_id AND
            senses_lemgrams.sense_id = ?""",
            (sense_rowid,))]
        return sense, primary, tuple(secondary), tuple(lemgrams)

    def db_get_senses_by_lemgram(self, lemgram):
        return tuple([self.get_sense(sense) for sense, in self.conn.execute(
            """SELECT sense FROM senses, senses_lemgrams, lemgrams WHERE
            senses.rowid = senses_lemgrams.sense_id AND
            lemgrams.rowid = senses_lemgrams.lemgram_id AND
            lemgram = ?""",
            (lemgram,))])

    def db_get_senses_by_primary(self, primary):
        return tuple([self.get_sense(sense) for sense, in self.conn.execute(
            "SELECT sense FROM senses WHERE mother = ?", (primary,))])

    def db_get_senses_by_secondary(self, secondary):
        return tuple([self.get_sense(sense) for sense, in self.conn.execute(
            """SELECT sense FROM senses, senses_secondary WHERE
            senses.rowid = sense_id AND father = ?""", (secondary,))])

    def get_sense(self, sense_id):
        return _get_cached(self.senses_cache, sense_id, self.db_get_sense)

    def get_lemgram(self, lemgram_id):
        return _get_cached(self.lemgrams_cache, lemgram_id,
                           self.db_get_lemgram)

    def get_forms_by_lemgram(self, lemgram_id):
        return _get_cached(self.lemgram_forms_cache, lemgram_id,
                           self.db_get_forms_by_lemgram)

    def get_senses_by_lemgram(self, lemgram_id):
        return _get_cached(self.lemgram_senses_cache, lemgram_id,
                           self.db_get_senses_by_lemgram)

    def get_lemgrams_by_form(self, form):
        return _get_cached(self.form_lemgrams_cache, form,
                           self.db_get_lemgrams_by_form)

    def get_lemgrams_by_gf(self, gf):
        return _get_cached(self.gf_lemgrams_cache, gf,
                           self.db_get_lemgrams_by_gf)

    def get_ancestors(self, sense_id, levels=1000):
        if sense_id == 'PRIM..1':
            return set()
        if levels <= 0:
            return set()
        _, primary, secondary, lemgrams = self.get_sense(sense_id)
        ancestors = set(secondary) if primary == 'PRIM..1' else set((primary,) + secondary)
        if levels == 1:
            return ancestors
        ancestors |= self.get_ancestors(primary, levels-1)
        for s in secondary:
            ancestors |= self.get_ancestors(s, levels-1)
        return ancestors
