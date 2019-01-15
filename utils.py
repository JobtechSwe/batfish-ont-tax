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
