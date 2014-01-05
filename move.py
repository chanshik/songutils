# coding: utf-8

import os
import sys

reload(sys)
sys.setdefaultencoding('utf8')

import mutagen
from colorama import init, Fore
init()

def is_music_file(filename):
    """
    Find a song file using extension.
    """
    valid_extensions = [u"flac", u"mp3", u"m4a"]

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


def make_new_path(save_path, song_info, ext):
    """
    Create artist/album folder.

    Return: [save_path]/[artist]/[album]/[title] path.
    """
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    album = song_info['album']
    disc_number = song_info['discnumber']
    track_number = song_info['tracknumber']
    title = song_info['title']
    album_artist = song_info['albumartist']
    artist = song_info['artist']

    if album_artist:
        artist_path = save_path + "/" + album_artist
        artist = album_artist
    else:
        artist_path = save_path + "/" + song_info['artist']

    if not os.path.exists(artist_path):
        print "Creating " + artist_path
        os.mkdir(artist_path)

    album_path = artist_path + "/" + song_info['album']

    if not os.path.exists(album_path):
        print "Creating " + album_path
        os.mkdir(album_path)

    if track_number:
        if disc_number:
            full_path = u"%s/%s/%s/%1d-%02d. %s.%s" % (
                save_path, artist, album, disc_number, track_number, title, ext)
        else:
            full_path = u"%s/%s/%s/%02d. %s.%s" % (save_path, artist, album, track_number, title, ext)
    else:
        full_path = u"%s/%s/%s/%s.%s" % (save_path, artist, album, title, ext)

    return full_path


def is_valid_meta(meta):
    """
    Check minimum required meta information exists.

    ID3v1 - title, artist, album (required)
            albumartist, discnumber tracknumber (optional)
    ID3v2 - TIT2, TPE1, TALB (required)
            TPE2, TPOS, TRCK (optional)
    m4a   - \xa9nam, \xa9ART, \xa9alb (required)
            aART, disk, trkn (optional)

    Return: True if meta has minium required attributes.
    """
    ID3v1_tags = ['title', 'artist', 'album']
    ID3v2_tags = ['TIT2', 'TPE1', 'TALB']
    m4a_tags = ['\xa9nam', '\xa9ART', '\xa9alb']

    if meta is None:
        return False

    is_ID3v1 = 'title' in meta
    is_ID3v2 = 'TALB' in meta
    try:
        is_m4a = '\xa9nam' in meta
    except UnicodeError:
        is_m4a = False

    if not is_ID3v1 and not is_ID3v2 and not is_m4a:
        return False

    if is_ID3v1:
        for tag in ID3v1_tags:
            if not tag in meta:
                return False
    elif is_ID3v2:
        for tag in ID3v2_tags:
            if not tag in meta:
                return False
    elif is_m4a:
        for tag in m4a_tags:
            if not tag in meta:
                return False

    return True


def extract_info_from_meta(meta):
    if meta is None:
        return False

    is_ID3v1 = 'title' in meta
    is_ID3v2 = 'TALB' in meta
    try:
        is_m4a = meta.has_key('\xa9nam')
    except UnicodeError:
        is_m4a = False

    if not is_ID3v1 and not is_ID3v2 and not is_m4a:
        return None

    song_info = {}

    if is_ID3v1:
        song_info = {'title': meta['title'][0], 'artist': meta['artist'][0], 'album': meta['album'][0],
                     'albumartist': meta['albumartist'][0] if 'albumartist' in meta else None,
                     'discnumber': int(meta['discnumber'][0]) if 'discnumber' in meta else None,
                     'tracknumber': int(meta['tracknumber'][0]) if 'tracknumber' in meta else None}

    elif is_ID3v2:
        song_info = {'title': meta['TIT2'][0], 'artist': meta['TPE1'][0], 'album': meta['TALB'][0],
                     'albumartist': meta['TPE2'][0] if 'TPE2' in meta else None,
                     'discnumber': int(meta['TPOS'][0]) if 'TPOS' in meta else None,
                     'tracknumber': int(meta['TRCK'][0]) if 'TRCK' in meta else None}

    elif is_m4a:
        song_info = {'title': meta['\xa9nam'][0], 'artist': meta['\xa9ART'][0], 'album': meta['\xa9alb'][0],
                     'albumartist': meta['aART'][0] if 'aART' in meta else None,
                     'discnumber': int(meta['disk'][0]) if 'disc' in meta else None,
                     'tracknumber': int(meta['trkn'][0][0]) if 'trkn' in meta else None}

    # Replace '/' character to '-' for valid file and directory name.
    if "/" in song_info['title']:
        song_info['title'] = song_info['title'].replace('/', '-')

    return song_info


def move(home_path, save_path):
    """
    Move song files in home directory to [save_path]/[artist]/[album]/[title]
    """

    files = os.listdir(u"%s" % home_path)

    for filename in files:
        if os.path.isdir(home_path + "/" + filename):
            print "Directory: " + filename
            move(home_path + "/" + filename, save_path)
            continue

        if not is_music_file(filename):
            print Fore.RED + "Not a music file: " + filename + Fore.RESET
            continue

        meta, name, ext = get_basic_info(home_path, filename)

        if not is_valid_meta(meta):
            print Fore.RED + "No meta information: " + filename + Fore.RESET
            continue

        song_info = extract_info_from_meta(meta)
        if not song_info:
            print Fore.RED + "No meta information: " + filename + Fore.RESET
            continue

        if song_info['album'] == '' or song_info['artist'] == '' or song_info['title'] == '':
            continue

        old_path = home_path + "/" + filename
        new_path = make_new_path(save_path, song_info, ext)

        # print old_path + "\n --> " + Fore.BLUE + new_path + Fore.RESET
        try:
            os.rename(old_path, new_path)
        except OSError, e:
            print Fore.RED + "Error: " + str(e)
            print "  From: " + old_path
            print "  To: " + new_path


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: ")
        print("  python move.py [Music Home Directory] [To Save Directory]")

        sys.exit(1)

    move(sys.argv[1], sys.argv[2])
