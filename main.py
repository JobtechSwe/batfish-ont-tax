def open_file(filename):
    with open(filename, "r") as fin:
        data = fin.read()
        data = data.lower()
        return data


def string_to_list(text):
    the_list = text.split("\n")
    return the_list


def clean_text(a_list):
    no_trailing_spaces = map(lambda i: i.strip(), a_list)
    no_empty_items = filter(lambda i: i != i.isspace(), no_trailing_spaces)
    cleaned_text = filter(lambda i: i != "", no_empty_items)
    return cleaned_text


def match_strings(list_w_terms, reference_file):
    set1 = set(list_w_terms)
    set2 = set(reference_file)
    matches = set1.intersection(set2)
    difference1 = set1.difference(set2)
    difference2 = set2.difference(set1)
    print("Matches:", len(matches))
    print("Number matching in list with terms:", len(difference1))
    print("Number matching in reference file:", len(difference2))


if __name__ == "__main__":
    legacy = open_file("recources/occupations_from_legacy_taxonomy.txt")
    ontology = open_file("recources/ontology_all_occupations.txt")
    legacy_occupations = string_to_list(legacy)
    ontology_occupations = string_to_list(ontology)
    cleaned_legacy = clean_text(legacy_occupations)
    cleaned_ontology = clean_text(ontology_occupations)
    match_strings(cleaned_ontology, cleaned_legacy)
