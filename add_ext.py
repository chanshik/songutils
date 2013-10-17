import os
import sys


def add_ext_one(file_path, ext):
    new_path = file_path + "." + ext

    print "%s --> %s" % (file_path, new_path)
    os.rename(file_path, new_path)


def add_ext(home_path, ext):
    files = os.listdir(home_path)

    for filename in files:
        full_path = home_path + "/" + filename

        if os.path.isdir(full_path):
            add_ext(full_path, ext)
            continue

        add_ext_one(full_path, ext)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "Usage: "
        print "  python add_ext.py [Home Directory] [Extension]"

        sys.exit(1)

    add_ext(sys.argv[1], sys.argv[2])