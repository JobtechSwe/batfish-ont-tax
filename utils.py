def open_file(filename):
    """
    Open file and return content
    :param filename: Full path to file as a string
    :return: A string with file content, all lower case
    """
    with open(filename, "r") as fin:
        data = fin.read()
        data = data.lower()
        return data


def string_to_list(text):
    """
    Convert a string to a list, splitting on line break
    :param text: A string
    :return: A list
    """
    the_list = text.split("\n")
    return the_list


def clean_text(a_list):
    """
    Remove trailing spaces after list items,
    remove list elements only containing a space,
    remove empty list elements
    :param a_list: A list
    :return: A cleaned list
    """
    no_trailing_spaces = map(lambda i: i.strip(), a_list)
    no_empty_items = filter(lambda i: i != i.isspace(), no_trailing_spaces)
    cleaned_text = filter(lambda i: i != "", no_empty_items)
    return cleaned_text
