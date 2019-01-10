def open_file(filename):
    with open(filename, "r") as fin:
        data = fin.read()
        return data


def clean_text(text):
    lower_text = text.lower()
    return lower_text

def string_to_list(text):
    the_list = text.split("\n")
    the_list = map(lambda i: i.strip(), the_list)
    the_list = filter(lambda i: i != i.isspace(), the_list)
    the_list = filter(lambda i: i != "", the_list)
    return the_list


def match_strings(list_w_terms, reference_file):
    set1 = set(list_w_terms)
    set2 = set(reference_file)
    matches = set1.intersection(set2)
    difference1 = set1.difference(set2)
    difference2 = set2.difference(set1)
    print("Matches:", len(matches))
    print("Not matchning in list with terms:", len(difference1))
    print("Not matchning in reference file:", len(difference2))


if __name__ == "__main__":
    legacy = open_file("recources/occupations_from_legacy_taxonomy.txt")
    ontology = open_file("recources/ontology_all_occupations.txt")
    lower_legacy = clean_text(legacy)
    lower_ontology = clean_text(ontology)
    legacy_occupations = string_to_list(lower_legacy)
    ontology_occupations = string_to_list(lower_ontology)
    match_strings(ontology_occupations, legacy_occupations)

