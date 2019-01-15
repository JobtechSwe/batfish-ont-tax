import exact_matches
import compound_splitter

tax_file = "resources/occupations_from_legacy_taxonomy.txt"  # path to file with words from Taxonomy
dm_file = "resources/ontology_all_occupations.txt"  # path to file with words from data mining
testfile = "resources/testdata.txt"

if __name__ == "__main__":
    #matched_words, not_matched_dm_words, not_matched_t_words = exact_matches.match(tax_file, dm_file)
    compound_splitter.split(testfile)
