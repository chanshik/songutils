import os
import sys
import unicodedata
import mutagen


def rename(dir_path):
    """
    Rename all files in dir_path to album_title_artist

    album, title, artist data extract from file itself using mutagen library.
    """

    reload(sys)
    sys.setdefaultencoding('utf8')

    files = os.listdir(u"%s" % dir_path)

    for filename in files:

        meta = mutagen.File(dir_path + "/" + filename)
        name = filename[:filename.rindex(".")]
        ext = filename[filename.rindex(".") + 1:]

        old_name = u"%s.%s" % (name, ext)
        old_name = unicodedata.normalize('NFC', old_name)
        new_name = u"%s_%s_%s.%s" % (meta['album'][0], meta['title'][0], meta['artist'][0], ext)

        old_path = dir_path + "/" + filename
        new_path = dir_path + "/" + new_name

        if old_name == new_name:
            continue

        print("[%s]\n ---> [%s]" % (old_path, new_path))

        try:
            os.rename(old_path, new_path)
        except OSError, e:
            print "  %s skipped: %s" % (old_path, str(e))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: ")
        print("  python rename.py [Directory]")

        sys.exit(1)

    rename(sys.argv[1])