
import os, sys, shutil, win32file, re, time, unicodedata, random

from mutagen.id3 import ID3
from mutagen.mp3 import MP3
from mutagen.apev2 import APEv2
import mutagen.id3

from django.conf import settings

DRIVES = {  'X:/': [ '0','A','B','C','D','E','F','G'],
            'Y:/': [ 'H','I','J','K','L','M','N','O', 'P','Q','R','S','T','U','V','W','X','Y','Z'],
            'Z:/': [ 'OST', 'VA']}

def move_new_folders(drive, letter):
    problems = []
    moved = []
    folders = []
    original_letter = letter
    original_drive = drive

    folders = os.listdir(drive + letter + '/')
    for folder in folders:
        letter = folder[0].upper()
        if letter == 'T':
            if len(folder) > 4:
                if folder[1].upper() == 'H' and folder[2].upper() == 'E':
                    if folder[3] == '-' or folder[3] == '.':
                        if is_number(folder[4].upper()):
                            letter = '0'
                        else:
                            letter = folder[4].upper()
        elif is_number(folder[0].upper()):
            letter = '0'

        elif str(folder).startswith('VA-') or str(folder).startswith('VA.') or str(folder).startswith('VARIOUS-') or str(folder).startswith('VARIOUS.ARTIST'):
            letter = 'VA'
        elif str(folder).startswith('SOUNDTRACK') or str(folder).startswith('OST') or str(folder).startswith('ORIGINAL.SOUNDTRACK'):
            letter = 'OST'
        
        if original_letter != letter:
            if letter in DRIVES['X:/']: drive = 'X:/'
            else: drive = 'Y:/'
            try:
                if original_drive == drive:
                    win32file.MoveFile(original_drive+original_letter+'/'+folder, drive+letter+'/'+folder)
                    #print original_drive+original_letter+'/'+folder, 'moved to\n', drive+letter+'/'+folder
                    moved.append(folder)
                else:
                    win32file.MoveFile(original_drive+original_letter+'/'+folder, original_drive+'MOVE/'+folder)
                    moved.append(folder)

            except:
                #print 'FAILED ',original_drive+original_letter+'/'+folder, 'moved to\n', drive+letter+'/'+folder
                try:
                    if original_drive == drive:
                        win32file.MoveFile(original_drive+original_letter+'/'+folder, drive+letter+'/'+folder+str(random.randrange(1, 100000)))
                        moved.append(folder)
                    else:
                        win32file.MoveFile(original_drive+original_letter+'/'+folder, original_drive+'MOVE/'+folder+str(random.randrange(1, 100000)))
                        moved.append(folder)
                except:
                    problems.append(folder)
                            
    return problems, moved
       
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def get_folder_names (directory):
    folder_names = []
    counter = 0
    for root, dirs, files in os.walk(directory):
        for dir in dirs:
            folder_names.append(str(dir))
    return folder_names


def folder_has_rated_music(folder):
    song_list = get_song_files(os.listdir(folder))
    for song in song_list:
        id3 = ID3(folder+'/'+song)
        if get_rating(id3) > 1:
            return True
    
    return False

def get_song_files(file_list):
    song_list = []
    
    for song in file_list:
        if song.rsplit('.')[-1].lower() == 'mp3' or song.rsplit('.')[-1].lower() == 'flac':
            song_list.append(song)
    
    return song_list


def get_rating(id3):
    ratings = id3.getall('POPM')
    if ratings:
        rating = ratings[0].rating
        if rating == 255:
            return 5
        elif rating < 255 and rating >= 196:
            return 4
        elif rating < 196 and rating >= 128:
            return 3
    return 0


def get_artist_from_id3(id3):
    
    album_artist_names=id3.getall('TPE2')
    album_artist_names2=id3.getall('TPE1')

    lead_artist = ''
    contributing_artist = ''

    # import pdb; pdb.set_trace();

    try: 
        lead_artist = album_artist_names[0].text
    except:
        pass

    if lead_artist:
        return lead_artist[0].encode('ascii','ignore')

    try: 
        contributing_artist = album_artist_names2[0].text
    except:
        pass

    if contributing_artist:
        return contributing_artist[0].encode('ascii','ignore')
    else:
        return ''

def removeEmptyFolders(path):
    if not os.path.isdir(path):
        return

    # remove empty subfolders
    files = os.listdir(path)
    if len(files):
        for f in files:
            fullpath = os.path.join(path, f)
            if os.path.isdir(fullpath):
                removeEmptyFolders(fullpath)

    # if folder empty, delete it
    files = os.listdir(path)
    if len(files) == 0:
        print "Removing empty folder:", path
        os.rmdir(path)
        