from spyro_compound_splitting import compound_splitter
import exact_matches

tax_file = "resources/occupations_from_legacy_taxonomy.txt"  # path to file with words from Taxonomy
dm_file = "resources/ontology_all_occupations.txt"  # path to file with words from data mining
testfile = "resources/testdata.txt"

if __name__ == "__main__":
    matched_words, not_matched_dm_words, not_matched_t_words = exact_matches.match(tax_file, dm_file)
    for word in not_matched_t_words:
        compound_splitter.do_split(word, "NN")
