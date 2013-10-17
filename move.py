# coding: utf-8

import os
import sys
import mutagen


def is_music_file(filename):
    """
    Find a song file using extension.
    """
    valid_extensions = [u"flac", u"mp3", u"m4a", u"ape"]

    for ext in valid_extensions:
        if filename.lower().strip().endswith(ext):
            return True

    return False


def get_basic_info(home_path, filename):
    """
    Get basic information about the song file meta, name, extension.

    Return: (meta, name, ext)
    """
    meta = mutagen.File(home_path + "/" + filename)
    name = filename[:filename.rindex(".")]
    ext = filename[filename.rindex(".") + 1:]

    return meta, name, ext


def make_new_path(save_path, artist, album, album_artist, title, track_number, ext):
    """
    Create artist/album folder.

    Return: [save_path]/[artist]/[album]/[title] path.
    """
    if album_artist != '':
        artist_path = save_path + "/" + album_artist
        artist = album_artist
    else:
        artist_path = save_path + "/" + artist

    if not os.path.exists(artist_path):
        print "Creating " + artist_path
        os.mkdir(artist_path)

    album_path = save_path + "/" + artist + "/" + album

    if not os.path.exists(album_path):
        print "Creating " + album_path
        os.mkdir(album_path)

    if track_number:
        return u"%s/%s/%s/%02d. %s.%s" % (save_path, artist, album, track_number, title, ext)
    else:
        return u"%s/%s/%s/%s.%s" % (save_path, artist, album, title, ext)


def is_valid_meta(meta):
    """
    Return: True if meta has 'album', 'artist', 'title' keys.
    """
    if meta is None:
        return False

    if not 'album' in meta or not 'artist' in meta or not 'title' in meta:
        return False

    if not 'albumartist' in meta or not 'tracknumber' in meta:
        return False

    return True


def move(home_path, save_path):
    """
    Move song files in home directory to [save_path]/[artist]/[album]/[title]
    """
    reload(sys)
    sys.setdefaultencoding('utf8')

    files = os.listdir(u"%s" % home_path)

    for filename in files:
        if os.path.isdir(home_path + "/" + filename):
            print "Directory: " + filename
            move(home_path + "/" + filename, save_path)
            continue

        if not is_music_file(filename):
            print "Not a music file: " + filename
            continue

        meta, name, ext = get_basic_info(home_path, filename)

        if not is_valid_meta(meta):
            print "No meta information: " + filename
            continue

        if meta['album'][0] == '' or meta['artist'][0] == '' or meta['title'][0] == '':
            continue

        album = meta['album'][0]
        album_artist = meta['albumartist'][0] if 'albumartist' in meta else ''
        artist = meta['artist'][0]
        title = meta['title'][0]
        track_number = int(meta['tracknumber'][0]) if 'tracknumber' in meta else None

        old_path = home_path + "/" + filename
        new_path = make_new_path(save_path, artist, album, album_artist, title, track_number, ext)

        print "%s ---> %s" % (old_path, new_path)
        os.rename(old_path, new_path)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: ")
        print("  python move.py [Music Home Directory] [To Save Directory]")

        sys.exit(1)

    move(sys.argv[1], sys.argv[2])