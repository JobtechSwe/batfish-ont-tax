from utils import open_file, string_to_list, clean_text
from spacy_swedish_lemmatizer_data import lookup
from functools import *
from pydash import *


def lookup_keys():
    return set(lookup.values())


def ilen(iterable):
    return reduce(lambda sum, element: sum + 1, iterable, 0)


def get_ontology():
    ontology = open_file("resources/ontology_all_occupations.txt")
    ontology_occupations = string_to_list(ontology)
    cleaned_legacy = clean_text(ontology_occupations)
    return cleaned_legacy


def get_taxonomy():
    a_file = open_file("resources/occupations_from_legacy_taxonomy.txt")
    strings = string_to_list(a_file)
    cleaned_strings = clean_text(strings)
    split_strings = map(split_slash, cleaned_strings)
    flatten_list = flatten(split_strings)
    return flatten_list


def split_slash(word):
    return  word.split("/")


def lookup_lemma(word):
    return lookup.get(word)


def lookup_list(a_list):
    hits = map(lookup_lemma, a_list)
    filtered_hits = filter(lambda string: bool(string), hits)
    return filtered_hits


# ilen(lookup_list(get_ontology())) # 126  #number of lookup matches in ontology


#  result = lookup_list(get_ontology())
#  print(*result, sep='\n')
#
#  result4 = lookup_list(get_taxonomy())
#  print(*result4, sep='\n')


def count_plain_match():
    lookup_vals = set(lookup.values())
    lookup_vals.intersection(set(get_ontology()))
    ontology_match = lookup_vals.intersection(set(get_ontology()))
    print(len(ontology_match))
    taxonomy_match = lookup_vals.intersection(set(get_taxonomy()))
    print(len(taxonomy_match))

# count_plain_match()
