
from subprocess import call


def open_file(filename):
    with open(filename, "r") as fin:
        data = fin.read()
        data = data.lower()
        return data


def string_to_list(text):
    the_list = text.split("\n")
    return the_list

def split(f):
    f_data = open_file(f)
    f_list = string_to_list(f_data)
    call(["ls", "-l"])
    call(['/home/sara/Utveckling/spyro/', 'pwd'])
    #call(["/home/sara/Utveckling/spyro"])
    #for term in f_list:
    #    call(["python splitter.py %s NN"])
