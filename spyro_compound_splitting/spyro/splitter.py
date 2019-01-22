from collections import defaultdict
import re
from spyro_compound_splitting.spyro import saldo as saldo_module


class Splitter:
    def __init__(self, saldo, min_seg=3, max_parts=4):
        self.saldo = saldo
        self.min_seg = min_seg
        self.max_parts = max_parts
        self.prefix_c = defaultdict(set)
        self.prefix_ci = defaultdict(set)
        self.prefix_cm = defaultdict(set)
        self.suffix = defaultdict(lambda: defaultdict(set))
        self.prefix_searched = set()
        self.suffix_searched = set()

    @staticmethod
    def combine(found, ends_at, j, history, depth):
        if depth <= 0:
            return
        for i, _, seg in ends_at[j]:
            if i == 0:
                found.append([seg] + history)
            else:
                Splitter.combine(found, ends_at, i, [seg] + history, depth - 1)

    def _has_prefix(self, prefix, initial):
        if prefix in self.prefix_searched:
            if prefix in self.prefix_c:
                return True
            if initial and (prefix in self.prefix_ci):
                return True
            if (not initial) and (prefix in self.prefix_cm):
                return True
        found = False
        for lemgram_id, pos, msd in \
                self.saldo.db_get_lemgrams_pos_msd_by_form(prefix):
            tags = msd.split()
            if 'c' in tags:
                self.prefix_c[prefix].add(lemgram_id)
                found = True
            elif 'ci' in tags:
                self.prefix_ci[prefix].add(lemgram_id)
                if initial:
                    found = True
            elif 'cm' in tags:
                self.prefix_cm[prefix].add(lemgram_id)
                if not initial:
                    found = True
        self.prefix_searched.add(prefix)
        return found

    POS_MAP = {'nn': 'NN', 'vb': 'VB', 'av': 'JJ', 'ab': 'AB'}

    def _has_suffix(self, suffix, pos):
        if suffix in self.suffix_searched:
            if suffix in self.suffix[pos]:
                return True
        found = False
        for lemgram_id, _, saldo_pos, _ in self.saldo.get_lemgrams_by_gf(suffix):
            suc_pos = Splitter.POS_MAP.get(saldo_pos)
            if suc_pos is None:
                continue
            self.suffix[suc_pos][suffix].add(lemgram_id)
            if suc_pos == pos:
                found = True
        self.suffix_searched.add(suffix)
        return found

    def is_semantic_compound(self, word, segs, pos):
        if not self._has_suffix(word, pos):
            return None

        def get_ancestors(lemgram_ids):
            senses = set()
            for lemgram_id in lemgram_ids:
                if lemgram_id is None:
                    continue
                senses |= set([
                    sense[0] for sense in
                    self.saldo.get_senses_by_lemgram(lemgram_id)])
            ancestors = set()
            for sense_id in senses:
                ancestors |= set(self.saldo.get_ancestors(sense_id, 2))
            return ancestors | senses

        word_ancestors = get_ancestors(
            [lemgram[0] for lemgram in self.saldo.get_lemgrams_by_form(word)])

        # TODO: make this more efficient by checking as we go
        seg_ancestors = get_ancestors(
            self.prefix_c.get(segs[0], set()) |
            self.prefix_ci.get(segs[0], set()))
        for middle in segs[1:-1]:
            seg_ancestors |= get_ancestors(
                self.prefix_c.get(middle, set()) |
                self.prefix_cm.get(middle, set()))
        seg_ancestors |= get_ancestors(
            self.suffix[pos].get(segs[-1], set()))
        return len(seg_ancestors & word_ancestors) > 0

    def analyze(self, word, pos, initial=True):
        ends_at = [[] for _ in range(len(word) + 1)]
        len_at = [None] * (len(word) + 1)
        len_at[0] = 0
        # Try to find candidates for the initial and middle segments
        for j in range(self.min_seg, len(word) - self.min_seg + 1):
            # First try the initial segment (the word itself is
            # compound-initial, as indicated by _initial_, otherwise this is
            # a middle segment)
            seg = word[:j]
            if self._has_prefix(seg, initial):
                ends_at[j].append((0, j, seg))
                len_at[j] = 1
            # Then try segments starting at position i
            for i in range(self.min_seg, j - self.min_seg + 1):
                if not ends_at[i]:
                    continue
                seg = word[i:j]
                if self._has_prefix(seg, False):
                    ends_at[j].append((i, j, seg))
                    if len_at[j] is None or len_at[j] > 1 + len_at[i]:
                        len_at[j] = 1 + len_at[i]
                # Does this segment start with a doubled letter?
                if not (word[i - 2] == word[i - 1]):
                    continue
                # If so, do the same thing as above, except 
                seg = word[i - 1] + seg
                if self._has_prefix(seg, False):
                    ends_at[j].append((i, j, seg))
                    if len_at[j] is None or len_at[j] > 1 + len_at[i]:
                        len_at[j] = 1 + len_at[i]
        # Try to find candidates for the final segment
        j = len(word)
        for i in range(self.min_seg, len(word) - self.min_seg + 1):
            if ends_at[i] == []:
                continue
            seg = word[i:]
            if self._has_suffix(seg, pos):
                ends_at[j].append((i, j, seg))
                if len_at[j] is None or len_at[j] > 1 + len_at[i]:
                    len_at[j] = 1 + len_at[i]
            # Does this segment start with a doubled letter?
            if not (word[i - 2] == word[i - 1]):
                continue
            seg = word[i - 1] + seg
            # If so, do the same thing as above, except 
            if self._has_suffix(seg, pos):
                ends_at[j].append((i, j, seg))
                if len_at[j] is None or len_at[j] > 1 + len_at[i]:
                    len_at[j] = 1 + len_at[i]
        if not ends_at[j]:
            return None
        if len_at[j] > 4:
            return None
        found = []
        Splitter.combine(found, ends_at, j, [], len_at[j])
        return found

    RE_WORD = re.compile(
        r'([a-zA-ZåäöéüÅÄÖÉÜ0-9]+-)*[a-zA-ZåäöéüÅÄÖÉÜ]+(:[a-zA-Z]+)?$')
    RE_DASH = re.compile(r'-+')

    def split(self, word, pos):
        is_not_word = Splitter.RE_WORD.match(word) is None
        parts = Splitter.RE_DASH.split(word)
        if len(parts) >= self.max_parts:
            return None
        elif len(parts) >= 2:
            if self._has_suffix(parts[-1], pos):
                if u"" in parts:
                    return None
                return [parts]
            if is_not_word:
                return None
            segs = self.analyze(parts[-1], pos, False)
            if segs is None:
                return [parts]
            else:
                return [parts[:-1] + seg for seg in segs]
        elif len(parts) == 1:
            if is_not_word:
                return None
            return self.analyze(word, pos)
        else:
            return None

    def import_prefixes(self, prefixes):
        for prefix in prefixes:
            if len(prefix) < self.min_seg:
                continue
            prefix = prefix.lower()
            self.prefix_c[prefix].add(None)


def do_split(compound, pos_tag):
    assert pos_tag in ['NN', 'PM', 'VB', 'JJ', 'AB']
    saldo_object = saldo_module.SALDO()
    splitter = Splitter(saldo_object)
    splits = splitter.split(compound, pos_tag)
    print(splits)
    if splits:
        for segments in splits:
            print(splitter.is_semantic_compound(compound, segments, pos_tag), segments)
