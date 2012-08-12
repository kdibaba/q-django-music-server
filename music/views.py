from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core import serializers
from django.utils import simplejson
from django.contrib.auth.decorators import login_required
from django.conf import settings

from itertools import chain
from operator import attrgetter

from media.music.forms import *
from media.music.models import *
from media.music.utils import *

import os, sys, shutil, win32file, re, time, unicodedata, random

from mutagen.id3 import ID3
from mutagen.mp3 import MP3
from mutagen.apev2 import APEv2
import mutagen.id3


LETTERS = ['0','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z', 'VA', 'OST']
ALBUMS_HEAD = ['0','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
SET_RATING = {'0': 0, '1': 32, '2': 64, '3': 128,'4':196, '5':255}
GUEST_ACCESS = 25

@login_required
def music(request):
    theme = 'theme_white'
    letter_list = LETTERS
    albums_list = ALBUMS_HEAD
    

    if request.user.is_superuser or request.user.is_staff:
        album_art = len(Music_Album.objects.filter(album_art=True))
        artists_count = Music_Artist.objects.count()
        albums_count = Music_Album.objects.count()
        missing_album_art = int(albums_count) - album_art
        songs_count = Music_Song.objects.count()
    else:
        album_art = len(Music_Album.objects.filter(access="public").filter(album_art=True))
        artists_count = len(Music_Album.objects.filter(access="public").distinct("album_artist"))
        albums_count = Music_Album.objects.filter(access="public").count()
        missing_album_art = int(albums_count) - album_art
        songs_count = 0
        for album in Music_Album.objects.filter(access="public"):
            print album.album_artist_id
            songs_count += int(album.song_count)

    theme = 'theme_'+request.user.get_profile().theme
    return render_to_response('base.html', locals())

@login_required
def add_to_music_db(request):
    result = 0    
    catalog_drive_music('add')
    if request.is_ajax():
        mimetype = 'application/javascript'
        result = 1
        return HttpResponse(result, mimetype)
    else:
        return music(request)
    
@login_required
def rebuild_music_db(request):
    result = 0        
    catalog_drive_music('rebuild')
    if request.is_ajax():
        mimetype = 'application/javascript'
        result = 1
        return HttpResponse(result, mimetype)
    else:
        return music(request)
    
def music_admin(request):
    theme = 'theme_'+request.user.get_profile().theme
    letter_list = LETTERS
    albums_list = ALBUMS_HEAD
    msg = ''
    directory = ''
    directories = []
    string_file_list = []
    copies = []
    renamed_files = []
    file_list = []
    cataloged = []
    problems = []
    moved = []
    num_of_copies = 0
    duplicates_count = {}
    if request.method == 'POST':
        form = Drive_form(request.POST)
        if 'filter_nzbs' in request.POST:
            if request.POST['nzbs']:
                problems, duplicates_count = filter_nzbs(request.POST['nzbs'])
            else: problems.append('You forgot to give me the location of the nzbs!')
        elif 'rename_nzbs' in request.POST:
            if request.POST['nzbs']:
                problems, renamed_files = rename_nzbs(request.POST['nzbs'])
            else: problems.append('You forgot to give me the location of the nzbs!')
        elif 'rename_albums' in request.POST:
            if request.POST['albums']:
                problems, renamed_files = rename_albums(request.POST['albums'])
        elif 'move_new_folders' in request.POST:
            problems, moved = move_new_folders()
        elif 'update_album_art' in request.POST:
            update_album_art(request)
                
    else:
        form = Drive_form()
    return render_to_response('admin.html', locals())
    
    
def fix_albums (directory):
    
    albums = os.listdir(directory)
    try: 
        os.mkdir(directory+'0')
        os.mkdir(directory+'1')
    except: pass
    duplicates = []
    counter = 0
    for items in albums:
        if str(items).count('-') > 1:
            album = str(items)
            true_album = album.rsplit('-', 1)[0]
            for items2 in albums:
                if true_album in str(items2) and str(items) != str(items2):
                    
                    try: os.rename(directory+str(items2), directory+'0/'+str(items2))
                    except: print items, 'failed to move to 0\n'
                    
                    duplicates.append (str(items))
                    counter += 1
            
    for items in albums:
        if str(items).count('-') > 1:
            album = str(items)
            true_album_2 = album.split('-')[0] + '-' + album.split('-')[1]+'-'
            for items2 in albums:
                if true_album_2 in str(items2) and str(items) != str(items2) and 'AC-DC' not in true_album_2:
                    
                    try: os.rename(directory+str(items2), directory+'1/'+str(items2))
                    except: print items, 'failed to move to 1\n'
                    
                    duplicates.append (str(items))
                    counter += 1
                pass            
    
                
    return duplicates
    
def catalog_drive_music(type):
    if type == 'rebuild':
        Music_Song.objects.all().delete()
        Music_Artist.objects.all().delete()
        Music_Album.objects.all().delete()
        
    unknown_genre = Music_Genre.objects.filter(genre='unknown')
    if unknown_genre:
        unknown_genre = unknown_genre[0]
    else: 
        unknown_genre = Music_Genre.objects.create(genre='unknown')
        
    start_time = time.time()
    for letter in LETTERS: 
        print letter
        directory = settings.MUSIC_DIRECTORY + letter + "/"
        files = os.listdir(directory)
        
        current_albums = Music_Album.objects.filter(letter=letter)
        for current_album in current_albums:
            try: files.remove(current_album.folder)
            except: pass
        
        for file_object in files:
            print file_object
            album = ''
            final_folder_name = ''
            file = file_object.split('-')
            if file.__len__() > 1:
                album_length = 0
                album_year = 0
                album_size = 0
                album_artist = []
                album_genres = {}
                album_bitrates = 0
                try: songs = os.listdir(directory+file_object)
                except: 
                    print file_object, ' doesnt exist!'
                    continue
                if songs.__len__() < 1:
                    try:
                        win32file.MoveFile(directory+file_object, settings.MUSIC_DIRECTORY+'EMPTY/'+file_object)
                    except:
                        print 'Couldnt Move empty folder.'
                    continue
                final_folder_name = file[0].upper().replace(' ', '.')
                artist_name = file[0].replace('.', ' ')
                album_artist = Music_Artist.objects.filter(artist=artist_name)
                if not album_artist:
                    album_artist = Music_Artist.objects.create(artist=artist_name)
                else: album_artist = album_artist[0]
                
                final_folder_name += '-'+file[1].upper().replace(' ', '.')
                album_name = file[1].replace('.', ' ')
                
                album_art = True
                if 'Folder.jpg' not in songs:
                    album_art=False
                
                album = Music_Album.objects.create(album_genre=unknown_genre, album_artist=album_artist, album=album_name, folder=file_object, album_art=album_art, letter=letter)
                album_artist.letter = letter
                album_artist.save()
                id3_info = {}
                song_count = 0
                song_list = []
                for song in songs:
                    songs_in_album = []
                    #print file, ' ----- ', song
                    if song.rsplit('.')[-1].lower() == 'mp3':
                        song_length = 0
                        song_rating = 0
                        song_artist = ''
                        file_size = ''
                        try: 
                            id3 = ID3(directory+file_object+'/'+song)
                            property = MP3(directory+file_object+'/'+song)
                        except: continue
                        song_length = property.info.length
                        album_length += song_length
                        result = time.strftime('%M:%S', time.gmtime(song_length))
                        #print directory+file_object+'/'+song
                        file_size=os.path.getsize(directory+file_object+'/'+song)
                        album_size += file_size
                                                
                        # Song genre
                        genre=''
                        genres=id3.getall('TCON')
                        song_genre = unknown_genre
                        if genres:
                            genre = genres[0].text
                            if genre: 
                                genre = genre[0]
                                get_genre = Music_Genre.objects.filter(genre=genre)
                                if not get_genre:
                                    song_genre = Music_Genre.objects.create(genre=genre)
                                else: 
                                    song_genre = get_genre[0]
                                    if album_genres and song_genre in album_genres.keys():
                                        album_genres[song_genre] += 1
                                    else: album_genres[song_genre] = 0
                        
                        # bitrate
                        song_bitrate=''
                        song_bitrate=property.info.bitrate
#                        if song_bitrate: 
#                            album_bitrates += int(song_bitrate)
                                    
                        song_artist = album_artist
                        artist_names=id3.getall('TPE1')
                        if artist_names:
                            artist_name = artist_names[0].text
                            if artist_name:
                                artist_name = artist_name[0]
                                get_song_artist = Music_Artist.objects.filter(artist=artist_name)
                                if not get_song_artist:
                                    song_artist = Music_Artist.objects.create(artist=artist_name)
                                else: 
                                    song_artist = get_song_artist[0]
                            
                        if not album_year:
                            get_years = album_year=id3.getall('TDRC')
                            if get_years:
                                get_year = get_years[0].text
                                if get_year:
                                    album_year = get_year[0]

                        safe_song = unicode(song, errors='ignore').encode('utf-8')
                        if song != safe_song:
                            try:
                                win32file.MoveFile(directory+file_object+'/'+song, directory+file_object+'/'+safe_song)
                                print 'renamed ' + song + ' to ' + safe_song
                            except:
                                print 'filename is a duplicate'
                                continue
                            
                            
                        # Song title
                        title = safe_song
                        titles = id3.getall('TIT2')
                        if titles:
                            get_title = titles[0].text
                            if get_title:
                                title = get_title[0]
                                
                        song_rating=get_rating(id3)
                        song_list.append(Music_Song.objects.create(song_artist=song_artist, 
                                                                  song_genre=song_genre, 
                                                                  album=album, 
                                                                  filename=safe_song, 
                                                                  type=safe_song.rsplit('.')[-1],
                                                                  path=file_object,
                                                                  title=title,
                                                                  length=str(result),
                                                                  letter=letter,
                                                                  rating=song_rating,
                                                                  file_size=str(file_size),
                                                                  bitrate=song_bitrate
                                                                  ))
                        song_count += 1
                album.length = time.strftime('%M:%S', time.gmtime(album_length))
                album.song_count = song_count
                album.album_size = str(album_size)
                if album_genres: album.album_genre = max(album_genres, key=album_genres.get)
                
                if album_year: 
                    string_album_year = album_year.encode('ascii','ignore')
                    if string_album_year: 
                        album.year = int(string_album_year[0]+string_album_year[1]+string_album_year[2]+string_album_year[3])
                    if album.year < 1800 or album.year > 2020:
                        album.year = 0
                else: 
                    album.year = 0                
                if album.year != 0: final_folder_name += '-'+str(album.year) 
                
#                if album_bitrates: 
#                    overall_bitrate = album_bitrates / song_count
#                    if overall_bitrate:
#                        final_folder_name += '-'+str(overall_bitrate)
                # Rename the folder
                album.save()
                final_folder_name = file_string_rename(final_folder_name)
                try:
                    win32file.MoveFile(directory+file_object, directory+final_folder_name)
                    album.folder = final_folder_name
                    album.save()
                except:
                    saves = check_duplicate(directory, file_object, final_folder_name)
                    if saves != 'keep':
                        for songs in song_list:
                            songs.delete()
                        album.delete()
                
        print 'Took ', time.time() - start_time, ' to finish one iteration.'
    return #render_to_response('confirmation.html', locals())
 
def check_duplicate(directory, current, rename_to):
    current_file_list = get_song_files(os.listdir(directory+current))
    rename_to_file_list = get_song_files(os.listdir(directory+rename_to))
    for song in current_file_list:
        if song not in rename_to_file_list:
            try:
                if folder_has_rated_music(directory+current):
                    win32file.MoveFile(directory+rename_to, settings.MUSIC_DIRECTORY+'PARTIAL/'+rename_to)
                    return 'keep'
                else:
                    win32file.MoveFile(directory+current, settings.MUSIC_DIRECTORY+'PARTIAL/'+rename_to)
                    return ''                 
            except:
                try:
                    win32file.MoveFile(directory+current, settings.MUSIC_DIRECTORY+'PARTIAL/'+rename_to+'.'+str(random.randrange(1, 100)))
                except:
                    print 'Failed to move a partial duplicate album.'
            return
    
    for song in current_file_list:
        try:
            if folder_has_rated_music(directory+current):
                win32file.MoveFile(directory+rename_to, settings.MUSIC_DIRECTORY+'EXACT/'+rename_to)
                return 'keep'
            else:
                win32file.MoveFile(directory+current, settings.MUSIC_DIRECTORY+'EXACT/'+rename_to)
                return ''                 
        except:
            try:
                win32file.MoveFile(directory+current, settings.MUSIC_DIRECTORY+'EXACT/'+rename_to+'.'+str(random.randrange(1, 100)))
            except:
                print 'Failed to move an exact duplicate album.'
        return

    return ''

            
def update_album_art(request):
    letter_list = LETTERS
    albums_list = ALBUMS_HEAD
    existing_album_art = len(Music_Album.objects.filter(album_art=True))
    new_album_art = 0
    missing_album_art = Music_Album.objects.filter(album_art=False)
    for albums in missing_album_art: 
        try: 
            songs = os.listdir(settings.MUSIC_DIRECTORY + albums.letter + "/" + albums.folder)
            if 'Folder.jpg' in songs:
                new_album_art += 1
                albums.album_art = True
                albums.save()
        except: pass
        
    
    message = 'Album Art Updated<br/> Existing = ' + str(existing_album_art) + '<br />New = ' + str(new_album_art) + '<br />Missing = ' + str(len(missing_album_art))
    return render_to_response('confirmation.html', locals()) 


def filter_nzbs(path_to_nzbs):
    os.chdir(path_to_nzbs)
    all_nzbs = os.listdir('.')
    
    try:
        os.makedirs('exact_duplicate')
        os.makedirs('partial_duplicate')
    except:
        pass
        
    counter = 0
    progress_counter = 0
    copies = []
    string2 = ''
    albums_in_DB = Music_Album.objects.all()
    albums_in_collection_folder = os.listdir('D:\QmA\NZB\Music\Albums\Collection/')
    remove = ['-CDS-','.CDS.','-PROMO-','.CDS.','BOOTLEG','(CDS)','(BOOTLEG)']
    problems = []
    duplicates_count = {'exact': 0, 'partial': 0}
    
    for nzbs in all_nzbs:
        exists = Music_Album.objects.filter(folder=nzbs.rsplit('.NZB')[0])
        if exists:
            try:
                os.rename(path_to_nzbs+nzbs, path_to_nzbs+'exact_duplicate/'+nzbs)
                duplicates_count['exact'] += 1
            except:
                problems.append('Failed to move the duplicate file: '+ nzbs)
                
    for temp_nzbs in all_nzbs:
        nzbs = temp_nzbs.split('-')
        if len(nzbs) > 2:
            artist = nzbs[0].replace('.', ' ')
            album = nzbs[1].replace('.', ' ')
            exists = Music_Album.objects.filter(album_artist__artist__exact=artist).filter(album=album)
            if exists:
#                print 'For ', temp_nzbs, '\n', exists[0].folder
                try:
                    os.rename(path_to_nzbs+temp_nzbs, path_to_nzbs+'partial_duplicate/'+temp_nzbs)
                    duplicates_count['partial'] += 1
                except:
                    problems.append('Failed to move the duplicate file: '+ nzbs)                
            
#    for albums in albums_in_DB:
#        counter += 1
#        for nzbs in all_nzbs:
#            if albums.folder == nzbs.rsplit('.NZB')[0]:
#                print 'Found Match: \n', albums.folder, '\n',  nzbs.rsplit('.NZB')[0]
#                try:
#                    os.rename(path_to_nzbs+nzbs, path_to_nzbs+'exact_duplicate/'+nzbs)
#                    duplicates_count['exact'] += 1
#                except:
#                    problems.append('Failed to move the duplicate file: '+ nzbs)
#                break
#            else:
##                try:
##                    safe = albums.folder[15]
##                    if safe:
##                        if albums.folder in nzbs.rsplit('.NZB')[0]:
##                            try:
##                                os.rename(path_to_nzbs+nzbs, path_to_nzbs+'partial_duplicate/'+nzbs)
##                            except:
##                                print 'Failed to move the duplicate file.'
##                except:
##                    pass#print albums.folder, 'was not safe\n'
#
#                #More aggressive elimination of albums
#                try:
#                    name = albums.artist.artist.replace(' ','.')+'-'+albums.album.replace(' ','.')
#                    safe = name[14]
#                    if name in nzbs.rsplit('.NZB')[0]:
#                        print 'Found Partial Match: \n', albums.folder, '\n',  nzbs.rsplit('.NZB')[0]
#                        try:
#                            os.rename(path_to_nzbs+nzbs, path_to_nzbs+'partial_duplicate/'+nzbs)
#                            duplicates_count['partial'] += 1
#                        except:
#                            problems.append('Failed to move the duplicate file: '+ nzbs)
#                        break
#                except:
#                    pass#print albums.folder, 'was not safe\n'
#                
#        if counter > 1000:
#            return problems, duplicates_count
                                
    return problems, duplicates_count

def rename_albums(path_to_albums):
    renamed_files = []
    problems = []
    
    for letter in LETTERS:
        problem, renamed_file = rename_nzbs(path_to_albums+letter+'/', albums=False)
        problems += problem
        renamed_files += renamed_file
    
    return problems, renamed_files

def file_string_rename(string):
    string2 = string.replace('[', '.')
    string2 = string2.replace('.-.', '-')
    string2 = string2.replace('--', '-')
    string2 = string2.replace('-.', '-')
    string2 = string2.replace('.-', '-')
    string2 = string2.replace('..', '.')
    if string2[0] == '.':
        string2 = string2.lstrip('.')
    if string[0] == '-':
        string2 = string2.lstrip('-')

    return string2

def rename_nzbs(path_to_nzbs, albums=True):
    renamed_files = []
    problems = []
    os.chdir(path_to_nzbs)
    all_nzbs = os.listdir('.')
    if albums:
        try:
            os.makedirs('failed')
        except:
            pass        
    
    HYPHENATE = ['GL8', 'VBR', '2CD', '3CD', '4CD', '5CD', '6CD', '7CD']
    #Rename all the nzbs
    for nzbs in all_nzbs:
        string = str(nzbs)
        string2 = string.replace('[', '.')
        
        string2 = string2.upper()
        string2 = string2.replace(']', '.')
        string2 = string2.replace('.NZB.nzb', '.nzb')
        string2 = string2.replace('_', '.')
        string2 = string2.replace(']', '.')
        string2 = string2.replace('(', '.')
        string2 = string2.replace(')', '.')
        string2 = string2.replace('.bt.', '.')
        string2 = string2.replace('.BT.', '.')
        string2 = string2.replace('JAY-Z', 'JAY.Z')
        string2 = string2.replace('T-PAIN', 'T.PAIN')
        string2 = string2.replace('Z-RO', 'Z.RO')
        string2 = string2.replace('Q-TIP', 'Q.TIP')
        string2 = string2.replace('NE-YO', 'NE.YO')
        string2 = string2.replace('AC-DC', 'ACDC')
        string2 = string2.replace('AC.DC', 'ACDC')
        string2 = string2.replace('.VOL.', '.VOLUME.')
        for words in HYPHENATE:
            string2 = string2.replace('.'+words+'.', '-'+words+'-')
            string2 = string2.replace('.'+words+'-', '-'+words+'-')
            string2 = string2.replace('-'+words+'.', '-'+words+'-')
            
        string2 = string2.replace('\'', '.')
        string2 = string2.replace(',', '.')
        string2 = string2.replace('{', '.')
        string2 = string2.replace('}', '.')
        string2 = string2.replace(' ', '.')
        string2 = string2.replace('_', '.')
        string2 = string2.replace('.-.', '-')
        string2 = string2.replace('--', '-')
        string2 = string2.replace('-.', '-')
        string2 = string2.replace('.-', '-')
        string2 = string2.replace('..', '.')
        string2 = string2.replace('-NZB', '.NZB')
        
        if string2.startswith('000-'):
            string2 = string2.replace('000-', '')
        if string2.startswith('00-'):
            string2 = string2.replace('00-', '')
        if string2.startswith('0-'):
            string2 = string2.replace('0-', '')
            
        if string2[0] == '.':
            string2 = string2.lstrip('.')
        if string[0] == '-':
            string2 = string2.lstrip('-')
            
        if string != string2:
            try:
                win32file.MoveFile(path_to_nzbs+nzbs, path_to_nzbs+string2)
                renamed_files.append(nzbs + ' to ' + string2)
            except:
                problems.append('Renaming of ' + nzbs + ' to ' + string2 + ' failed')
                if albums: 
                    try:
                        win32file.MoveFile(path_to_nzbs+nzbs, path_to_nzbs+'failed/'+string2)
                    except:
                        problems.append('Moving a file that failed to rename also Failed. WOW.')
    
    return problems, renamed_files

@login_required
def albums(request, letter):
    if request.user.is_superuser or request.user.is_staff:
        if letter == 'all':
            all_albums = Music_Album.objects.all()
        elif letter == '0':
            all_albums = Music_Album.objects.filter(album__regex=r'\d')
        else:
            letter_albums = Music_Album.objects.filter(album__startswith=letter).exclude(album__startswith='THE ')
            albums_with_the = Music_Album.objects.filter(album__startswith='THE '+letter)
            all_albums = sorted(chain(letter_albums, albums_with_the),key=attrgetter('album'))
    else:
        if letter == 'all':
            all_albums = Music_Album.objects.filter(access="public")
        elif letter == '0':
            all_albums = Music_Album.objects.filter(access="public").filter(album__regex=r'\d')
        else:
            letter_albums = Music_Album.objects.filter(access="public").filter(album__startswith=letter).exclude(album__startswith='THE ')
            albums_with_the = Music_Album.objects.filter(access="public").filter(album__startswith='THE '+letter)
            all_albums = sorted(chain(letter_albums, albums_with_the),key=attrgetter('album'))
    
    dictionary_albums = []
    for album in all_albums:
        album_info = {}
        album_info['artist'] = album.album_artist.artist
        album_info['artist_id'] = album.album_artist.id
        album_info['genre'] = album.album_genre.genre
        album_info['genre_id'] = album.album_genre.id
        album_info['pk'] = album.id
        album_info['album'] = album.album
        album_info['song_count'] = album.song_count
        album_info['letter'] = album.letter
        album_info['folder'] = album.folder
        album_info['album_art'] = album.album_art
        album_info['year'] = album.year
        album_info['album_size'] = album.get_album_size()
        dictionary_albums.append(album_info)
        
    if request.is_ajax():
        mimetype = 'application/javascript'
        albums = simplejson.dumps(dictionary_albums)
    return HttpResponse(albums, mimetype)

@login_required
def album_info(request, album_id):
    albuminfo = ''
    album = Music_Album.objects.get(id=album_id)
    if request.is_ajax():
        mimetype = 'application/javascript'
        albuminfo = serializers.serialize('json', Music_Album.objects.filter(id=album_id))
    return HttpResponse(albuminfo, mimetype)

@login_required
def album(request, album_id):
    original_album = Music_Album.objects.get(id=album_id)
    songs = Music_Song.objects.filter(album=original_album, type="mp3").order_by('filename')
    all_album = []
    album = {}
    album['pk'] = original_album.id 
    album['album'] = original_album.album 
    album['genre'] = original_album.album_genre.genre 
    album['genre_id'] = original_album.album_genre.id 
    album['folder'] = original_album.folder 
    album['letter'] = original_album.letter 
    album['year'] = original_album.year 
    album['song_count'] = original_album.song_count 
    album['artist'] = original_album.album_artist.artist 
    album['artist_id'] = original_album.album_artist.id 
    album['album_art'] = original_album.album_art
    album['album_size'] = original_album.get_album_size()
    album['songs'] = []
    for song in songs:
        song_dict = {}
        song_dict['pk']  =  song.id
        song_dict['filename']  =  song.filename
        song_dict['length']  =  song.length
        song_dict['title']  =  song.title
        song_dict['artist']  =  song.song_artist.artist
        song_dict['genre']  =  song.song_genre.genre
        song_dict['type']  =  song.type
        song_dict['path']  =  song.path
        song_dict['letter']  =  song.letter
        song_dict['rating']  =  song.rating
        song_dict['file_size']  =  song.get_file_size()
        album['songs'].append(song_dict)
    all_album.append(album)    
    if request.is_ajax():
        mimetype = 'application/javascript'
    return HttpResponse(simplejson.dumps(all_album), mimetype)


@login_required
def get_song(request, song_id):
    original_song = Music_Song.objects.get(id=song_id)
    song = {}
    song['pk'] = original_song.id 
    song['letter'] = original_song.letter 
    song['path'] = original_song.path 
    song['filename'] = original_song.filename 
    song['title'] = original_song.title 
    song['artist'] = original_song.song_artist.artist 
    if request.is_ajax():
        mimetype = 'application/javascript'
    return HttpResponse(simplejson.dumps(song), mimetype)

@login_required
def delete_album(request, album_id):
    album = Music_Album.objects.get(id=album_id)
    message = album.album_artist.id
    songs = Music_Song.objects.filter(album=album)
    shutil.move(settings.MUSIC_DIRECTORY+album.letter+'/'+album.folder, settings.MUSIC_DIRECTORY+'DELETED/')
    for song in songs:
        song.delete()
    album.delete()      
    if request.is_ajax():
        mimetype = 'application/javascript'
    return HttpResponse(message, mimetype)


@login_required
def albums_by_artist(request, artist_id):
    artist = Music_Artist.objects.get(id=artist_id)
    if request.user.is_superuser or request.user.is_staff:
        all_albums = Music_Album.objects.filter(album_artist=artist).order_by('album')
    else:
        all_albums = Music_Album.objects.filter(access="public").filter(album_artist=artist).order_by('album')
        
    if request.is_ajax():
        mimetype = 'application/javascript'
        albums = simplejson.dumps(albums_by_requirement(all_albums))
    return HttpResponse(albums, mimetype)


@login_required
def albums_by_year(request, year_id):
    if request.user.is_superuser or request.user.is_staff:
        all_albums = Music_Album.objects.filter(year=year_id).order_by('album')
    else:
        all_albums = Music_Album.objects.filter(access="public").filter(year=year_id).order_by('album')
        
    if request.is_ajax():
        mimetype = 'application/javascript'
        albums = simplejson.dumps(albums_by_requirement(all_albums))
    return HttpResponse(albums, mimetype)


@login_required
def albums_by_genre(request, genre_id):
    if request.user.is_superuser or request.user.is_staff:
        all_albums = Music_Album.objects.filter(album_genre=genre_id).order_by('album')
    else:
        all_albums = Music_Album.objects.filter(access="public").filter(album_genre=genre_id).order_by('album')
        
    if request.is_ajax():
        mimetype = 'application/javascript'
        albums = simplejson.dumps(albums_by_requirement(all_albums))
    return HttpResponse(albums, mimetype)

def albums_by_requirement(all_albums):
    dictionary_albums = []
    for album in all_albums:
        album_info = {}
        album_info['artist'] = album.album_artist.artist
        album_info['artist_id'] = album.album_artist.id
        album_info['genre'] = album.album_genre.genre
        album_info['genre_id'] = album.album_genre.id
        album_info['pk'] = album.id
        album_info['album'] = album.album
        album_info['song_count'] = album.song_count
        album_info['letter'] = album.letter
        album_info['folder'] = album.folder
        album_info['album_art'] = album.album_art
        album_info['year'] = album.year
        album_info['album_size'] = album.get_album_size()
        dictionary_albums.append(album_info)
    
    return dictionary_albums

@login_required
def artists(request, letter):
    if letter == 'all': get_artists = Music_Artist.objects.all().order_by('artist')
    else: get_artists = Music_Artist.objects.filter(letter=letter).order_by('artist')
        
    artists = []
    for get_artist in get_artists:
        try:
            artist = {}
            artist['pk'] = get_artist.id
            artist['name'] = get_artist.artist
            artist['song_count'] = 0
            artist['album_count'] = 0
            artist['albums'] = []
            if request.user.is_superuser or request.user.is_staff:
                get_albums = Music_Album.objects.filter(album_artist=get_artist.id).order_by('id')
            else:
                get_albums = Music_Album.objects.filter(access="public").filter(album_artist=get_artist.id).order_by('id')
            if get_albums:
                for get_album in get_albums:
                    album = {}
                    album['letter'] = get_album.letter
                    album['folder'] = get_album.folder
                    album['album_art'] = get_album.album_art
                    album['pk'] = get_album.id
                    
                    artist['song_count'] += get_album.song_count
                    artist['album_count'] += 1
                    artist['albums'].append(album)
                artists.append(artist)
        except:
            print 'excepted', get_artist.artist
    
    if request.is_ajax():
        mimetype = 'application/javascript'
        artists = simplejson.dumps(artists)
    return HttpResponse(artists, mimetype)   
    
    
@login_required
def rebuild(request, letter):
    Music_Artist.objects.filter(letter=letter).delete()
    catalog_drive_music('none')
    return HttpResponseRedirect('/#/artists/'+letter)
    
@login_required
def set_rating(request, song_id, rating):
    message = 0
    if request.user.username == 'kdibaba':
        song = Music_Song.objects.get(id=song_id)
        path_to_song = settings.MUSIC_DIRECTORY + song.letter +"/"+song.path+"/"+song.filename
        audio = ID3(path_to_song)
        key_found = False
        for key in audio.keys():
            if 'POPM' in key:
                key_found = True
                audio.getall('POPM')[0].rating=SET_RATING[str(rating)]
                audio.save()    
        if not key_found:
            print 'Creating the key'
            audio.add(mutagen.id3.POPM(email=u'Windows Media Player 9 Series', rating=SET_RATING[str(rating)]))
            audio.save()
        song.rating = rating
        song.save()
        message = 1
    if request.is_ajax():
        mimetype = 'application/javascript'
    return HttpResponse(message, mimetype)
 
@login_required
def get_profile_song_columns(request):
    columns = request.user.get_profile().song_table_columns
    
    if request.is_ajax():
        mimetype = 'application/javascript'
    return HttpResponse(simplejson.dumps(columns), mimetype)
    
@login_required    
def set_profile_song_columns(request):
    columns = request.user.get_profile()
    if request.GET['query'] in columns.song_table_columns:
        columns.song_table_columns = columns.song_table_columns.replace(';'+request.GET['query'], '')
        columns.save() 
    else:
        columns.song_table_columns = columns.song_table_columns+';'+request.GET['query']
        columns.save()
    if request.is_ajax():
        mimetype = 'application/javascript'
    return HttpResponse(mimetype)
     
@login_required    
def set_theme(request):
    profile = request.user.get_profile()
    profile.theme = request.GET['query']
    profile.save()
    if request.is_ajax():
        mimetype = 'application/javascript'
    return HttpResponse(mimetype)

@login_required    
def search_music_artists(request):
    start_time = time.time()
    get_artists = Music_Artist.objects.filter(artist__icontains=request.GET['query'])   
    artists = []
    for get_artist in get_artists:
        try:
            if request.user.is_superuser or request.user.is_staff:
                get_albums = Music_Album.objects.filter(album_artist=get_artist.id).order_by('id')
            else:
                get_albums = Music_Album.objects.filter(access="public").filter(album_artist=get_artist.id).order_by('id')

            if get_albums:
                artist = {}
                artist['pk'] = get_artist.id
                artist['name'] = get_artist.artist
                artist['song_count'] = 0
                artist['album_count'] = 0
                artist['albums'] = []
                for get_album in get_albums:
                    album = {}
                    album['letter'] = get_album.letter
                    album['folder'] = get_album.folder
                    album['album_art'] = get_album.album_art
                    album['pk'] = get_album.id
                    
                    artist['song_count'] += get_album.song_count
                    artist['album_count'] += 1
                    artist['albums'].append(album)
                artists.append(artist)
        except:
            print 'excepted'

    if request.is_ajax():
        mimetype = 'application/javascript'
        artists = simplejson.dumps(artists)
        print 'Artists search completed in ', time.time() - start_time
    return HttpResponse(artists, mimetype)
    
        
@login_required
def search_music_albums(request):
    start_time = time.time()
             
    if request.user.is_superuser or request.user.is_staff:           
        all_albums = Music_Album.objects.filter(album__icontains=request.GET['query'])   
    else:
        all_albums = Music_Album.objects.filter(access="public").filter(album__icontains=request.GET['query']) 

    dictionary_albums = []
    for album in all_albums:
        album_info = {}
        album_info['artist'] = album.album_artist.artist
        album_info['artist_id'] = album.album_artist.id
        album_info['genre'] = album.album_genre.genre
        album_info['genre_id'] = album.album_genre.id
        album_info['pk'] = album.id
        album_info['album'] = album.album
        album_info['song_count'] = album.song_count
        album_info['letter'] = album.letter
        album_info['folder'] = album.folder
        album_info['album_art'] = album.album_art
        album_info['year'] = album.year
        album_info['album_size'] = album.get_album_size()
        dictionary_albums.append(album_info)
        
    if request.is_ajax():
        mimetype = 'application/javascript'
        albums = simplejson.dumps(dictionary_albums)
        print 'Albums search completed in ', time.time() - start_time
    return HttpResponse(albums, mimetype)
      
      
@login_required
def search_music_songs(request):
    start_time = time.time()    
#    get_songs = Music_Song.objects.all()
#    all_songs = []
#    for items in get_songs:
#        if items.title:
#            if request.GET['query'].upper() in items.title.upper():
#                all_songs.append(items)
                      
                      
    all_songs = Music_Song.objects.filter(title__icontains=request.GET['query'])  
    dictionary_songs = []
    for song in all_songs:
        song_dict = {}
        song_dict['pk']  =  song.id
        song_dict['filename']  =  song.filename
        song_dict['length']  =  song.length
        song_dict['title']  =  song.title
        song_dict['artist']  =  song.song_artist.artist
        song_dict['genre']  =  song.song_genre.genre
        song_dict['type']  =  song.type
        song_dict['path']  =  song.path
        song_dict['letter']  =  song.letter
        song_dict['rating']  =  song.rating
        song_dict['file_size']  =  song.get_file_size()
        dictionary_songs.append(song_dict)
     
    if request.is_ajax():
        mimetype = 'application/javascript'
        albums = simplejson.dumps(dictionary_songs)
        print 'Songs search completed in ', time.time() - start_time
    return HttpResponse(albums, mimetype)


def upload_music(request):
    theme = 'theme_white'
    letter_list = LETTERS
    albums_list = ALBUMS_HEAD
    theme = 'theme_'+request.user.get_profile().theme
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES)
            return HttpResponseRedirect('/')
    else:
        form = UploadFileForm()
    return render_to_response('upload.html',  locals())     

def handle_uploaded_file(file):
    for key in file.keys():
        print file[key].name
        destination = open(settings.MUSIC_DIRECTORY+'UPLOADS/'+file[key].name, 'wb+')
        for chunk in file[key].chunks():
            destination.write(chunk)
        destination.close()
    return 

def copy_favs(request):
    existing_favs = []
    start = time.clock()
    
    for root, dirs, files in os.walk(settings.MUSIC_DIRECTORY+'/'+'FAVS'):
        for file in files:
            existing_favs.append(file)
            
    print 'Took ', time.clock() - start, ' to walk and find the files.'  


    five_star_songs = Music_Song.objects.filter(rating__gte=4)
    print 'Took ', time.clock() - start, ' to do the query.'
                
    
    print 'Five Star songs - ', len(five_star_songs)    
    print 'Existing Favs - ', len(existing_favs)

    five_star_songs = five_star_songs.exclude(filename__in=existing_favs)
    
      
    print 'Need to be copied - ', len(five_star_songs)
                        
    for songs in five_star_songs:
        try: 
            os.makedirs(settings.MUSIC_DIRECTORY+'/'+'FAVS'+'/'+songs.album.album_artist.artist)
        except: 
            pass
        try: 
            win32file.CopyFile(settings.MUSIC_DIRECTORY+songs.letter+'/'+songs.album.folder+'/'+songs.filename, 
                               settings.MUSIC_DIRECTORY+'/'+'FAVS'+'/'+songs.album.album_artist.artist+'/'+songs.filename, 0)
        except: 
            print songs.album.folder
    print 'Took ', time.clock() - start, ' to copy files.'
    return music(request)
    
@login_required    
def save_playlist(request):
    message = 0
    visible = True
    song_ids = request.GET['query'].split(',')
    playlist_name = request.GET['name']
    visibility = request.GET['visible']
    note = request.GET['note']
    
#    print request.GET['query'], request.GET['name'], request.GET['visible'], request.GET['note']
#    
    if visibility == 'false': visible = False
    
    existing_playlists = Music_Playlist.objects.filter(name=playlist_name, user=request.user)
    if not existing_playlists:
        for song in song_ids:
            Music_Playlist.objects.create(name=playlist_name, song=Music_Song.objects.get(id=int(song)), visible_to_others=visible, user=request.user, note=note)
            
        message = 1
    else:
        # There is a playlist with this name already.
        message = 2
    
    if request.is_ajax():
        mimetype = 'application/javascript'
        return HttpResponse(message, mimetype)
    else:
        render_to_response('save_playlist.html',  locals()) 

    
    

#def filter_nzbs_music (files, nzb_location):
#    
#    os.chdir(nzb_location)
#    try:
#        os.makedirs(nzb_location+'duplicate')
#    except:
#        pass
#    all_nzbs = os.listdir('.')
#    counter = 0
#    progress_counter = 0
#    copies = []
#    string2 = ''
#    all_albums = Music_Album.objects.all()
#    all_folders = []
#    for album in all_albums:
#        all_folders.append(str(album.folder))
#        #all_folders.append(str(album.artist.artist)+'-'+str(album.album))
#    
#    #all_albums = os.listdir('C:\QmA\NZB\Music\Albums\Collection')
#    #for album in all_albums:
#        #all_folders.append(str(album).replace('.nzb', ''))    
#    
#    remove = ['-CDS-','.CDS.','-PROMO-','.CDS.','BOOTLEG','(CDS)','(BOOTLEG)']
#    for nzbs in all_nzbs:
#        string = str(nzbs)
#        string2 = string.replace('[', '.')
#        string2 = string2.replace(']', '.')
#        string2 = string2.replace('.NZB.nzb', '.nzb')
#        string2 = string2.replace('..', '.')
#        string2 = string2.replace('..', '.')
#        string2 = string2.replace('..', '.')
#        if string != string2:
#            try:
#                print nzb_location+nzbs, ' renamed to ', nzb_location+string2
#                os.rename(nzb_location+nzbs, nzb_location+string2)
#            except:
#                print "Renaming the nzb failed\n"
#    
#    for folders in all_folders:
#        for nzbs in all_nzbs:
#            progress_counter = progress_counter + 1
#            if folders == str(nzbs).rsplit('.', 1)[0] or folders == str(nzbs).rsplit('.', 2)[0]:
#                try:
#                    os.rename(nzb_location+nzbs, nzb_location+'duplicate/'+nzbs)
#                    copies.append(str(nzbs))
#                    counter = counter + 1
#                except: print nzbs, ' duplicate file failed for\n', nzb_location+nzbs
#            else:
#                for items in remove: 
#                    if items in nzbs:
#                        try:
#                            os.rename(nzb_location+nzbs, nzb_location+'duplicate/'+nzbs)
#                            copies.append(str(nzbs))
#                            counter = counter + 1
#                        except: print nzbs, ' duplicate remove failed\n', nzb_location+nzbs
#            if progress_counter % 1000000 == 0:
#                print 'progress at ', progress_counter
#        
#    return counter, copies
    
    
    
    
    
    
    
    
    