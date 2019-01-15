import utils


def match_strings(list_w_terms, reference_file):
    set1 = set(list_w_terms)
    set2 = set(reference_file)
    matches = set1.intersection(set2)
    difference1 = set1.difference(set2)
    difference2 = set2.difference(set1)
    print("Matches:", len(matches))
    print("Number of words not matched in data mined words:", len(difference1))
    print("Number of words not matched in legacy taxonomy:", len(difference2))
    return matches, difference1, difference2


def match(t_file, dm_file):
    legacy = utils.open_file(t_file)
    ontology = utils.open_file(dm_file)
    legacy_occupations = utils.string_to_list(legacy)
    ontology_occupations = utils.string_to_list(ontology)
    cleaned_legacy = utils.clean_text(legacy_occupations)
    cleaned_ontology = utils.clean_text(ontology_occupations)
    return match_strings(cleaned_ontology, cleaned_legacy)
