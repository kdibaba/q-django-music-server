
import os, sys, shutil, win32file, re, time, unicodedata, random

from mutagen.id3 import ID3
from mutagen.mp3 import MP3
from mutagen.apev2 import APEv2
import mutagen.id3

from django.conf import settings


def move_new_folders():
    new_albums = 'NEW/'
    problems = []
    moved = []
    folders = os.listdir(settings.MUSIC_DIRECTORY + new_albums)
    print  folders
    for folder in folders:
        letter = folder[0].upper()
        if letter == 'T':
            if len(folder) > 4:
                if folder[1].upper() == 'H' and folder[2].upper() == 'E':
                    if folder[3] == '-' or folder[3] == '.':
                        letter = folder[4].upper()
        elif is_number(folder[0].upper()):
            letter = '0'
        elif letter == 'V':
            if len(folder) > 2:
                if folder[1].upper() == 'A':
                    if folder[2] == '-' or folder[2] == '.':
                        letter = 'VA'
        elif letter == 'O':
            if len(folder) > 3:
                if folder[1].upper() == 'S' and folder[2] == 'T':
                    if folder[3] == '-' or folder[3] == '.':
                        letter = folder[4].upper()
                    letter = 'OST'
        
        try:
            print settings.MUSIC_DIRECTORY+new_albums+folder, 'moved to', settings.MUSIC_DIRECTORY+letter+'/'+folder
            win32file.MoveFile(settings.MUSIC_DIRECTORY+new_albums+folder, settings.MUSIC_DIRECTORY+letter+'/'+folder)
            moved.append(folder)
        except:
            try:
                win32file.MoveFile(settings.MUSIC_DIRECTORY+new_albums+folder, settings.MUSIC_DIRECTORY+letter+'/'+folder+str(random.randrange(1, 100)))
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