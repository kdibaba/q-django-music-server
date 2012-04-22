from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.core import serializers
from django.utils import simplejson
from django.contrib.auth.decorators import login_required
from django.conf import settings

from media.music.forms import *
from media.music.models import *

import os, sys, shutil, win32file, re, time, unicodedata

from mutagen.id3 import ID3
from mutagen.mp3 import MP3
import mutagen.id3


LETTERS = ['0','A', 'B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z', 'VA']
SET_RATING = {'0': 0, '1': 32, '2': 64, '3': 128,'4':196, '5':255}
GUEST_ACCESS = 50

@login_required
def music(request):
    theme = 'theme_white'
    letter_list = LETTERS
    album_art = len(Music_Album.objects.filter(album_art=True))
    artists_count = Music_Artist.objects.count()
    albums_count = Music_Album.objects.count()
    missing_album_art = int(albums_count) - album_art
    songs_count = Music_Song.objects.count()
    
    theme = 'theme_'+request.user.get_profile().theme
    return render_to_response('base.html', locals())

@login_required
def add_to_music_db(request):
    result = 0    
    if request.is_ajax():
        mimetype = 'application/javascript'
        catalog_drive_music('add')
    return HttpResponse(result, mimetype)
    
@login_required
def rebuild_music_db(request):
    result = 0        
    if request.is_ajax():
        mimetype = 'application/javascript'
        catalog_drive_music('rebuild')
        result = 1
    return HttpResponse(result, mimetype)
        
#def handle_music_drive(request):
#    msg = ''
#    directory = ''
#    directories = []
#    string_file_list = []
#    copies = []
#    renamed_files = []
#    file_list = []
#    cataloged = []
#    problems = []
#    num_of_copies = 0
#    duplicates = []
#    if request.method == 'POST':
#        form = Drive_form(request.POST)
#        if 'catalog_drive' in request.POST:
#            catalog_drive_music()
#        elif 'filter_nzbs' in request.POST:
#            if request.POST['nzbs']:
#                num_of_copies, copies  = filter_nzbs_music (file_list, request.POST['nzbs'])
#            else: problems.append('You forgot to give me the location of the nzbs!')
#        elif 'fix_albums' in request.POST:
#            if request.POST['directory']:
#                duplicates  = fix_albums (request.POST['directory'])
#            else: problems.append('You forgot to give me the location of the nzbs!')
#                
#    else:
#        form = Drive_form()
#    return render_to_response('handle_music_drive.html', {  'form'              : form, 
#                                                            'cataloged'         : cataloged,
#                                                            'file_list'         : file_list,
#                                                            'problems'          : problems,
#                                                            'copies'            : copies,
#                                                            'num_of_copies'     : num_of_copies,
#                                                            'duplicates'        : duplicates,
#                                                            'msg'               : msg, } )    
    
def get_folder_names (directory):
    folder_names = []
    counter = 0
    for root, dirs, files in os.walk(directory):
        for dir in dirs:
            folder_names.append(dir)
    return folder_names

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
    
    for letter in LETTERS: 
        print letter
        directory = settings.MUSIC_DIRECTORY + letter + "/"
        files = get_folder_names(directory)
        for file_object in files:
            album = ''
            file = str(file_object).split('-')
            album_exists = Music_Album.objects.filter(folder=str(file_object))
            if file.__len__() > 1 and not album_exists:
                album_length = 0
                album_year = 0
                album_size = 0
                album_artist = []
                album_genres = {}
                try: songs = os.listdir(directory+str(file_object))
                except: 
                    print file_object, ' doesnt exist!'
                    continue
                
                artist_name = file[0].replace('.', ' ')
                album_artist = Music_Artist.objects.filter(artist=artist_name)
                if not album_artist:
                    album_artist = Music_Artist.objects.create(artist=artist_name)
                else: album_artist = album_artist[0]
                album_name = file[1].replace('.', ' ')
                
                album_art = True
                if 'Folder.jpg' not in songs:
                    album_art=False
                
                album = Music_Album.objects.create(album_genre=unknown_genre, album_artist=album_artist, album=album_name, folder=str(file_object), album_art=album_art, letter=letter)
                album_artist.letter = letter
                album_artist.save()
                id3_info = {}
                song_count = 0
                for song in songs:
                    #print file, ' ----- ', song
                    if song.rsplit('.')[-1] == 'mp3' or song.rsplit('.')[-1] == 'MP3':
                        song_length = 0
                        song_rating = 0
                        song_artist = ''
                        file_size = ''
                        try: 
                            id3 = ID3(directory+str(file_object)+'/'+song)
                            property = MP3(directory+str(file_object)+'/'+song)
                        except: continue
                        song_length = property.info.length
                        album_length += song_length
                        result = time.strftime('%M:%S', time.gmtime(song_length))
                        #print directory+str(file_object)+'/'+song
                        file_size=os.path.getsize(directory+str(file_object)+'/'+song)
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
                            win32file.MoveFile(directory+str(file_object)+'/'+song, directory+str(file_object)+'/'+safe_song)
                            print 'renamed ' + song + ' to ' + safe_song
                            
                            
                        # Song title
                        title = safe_song
                        titles = id3.getall('TIT2')
                        if titles:
                            get_title = titles[0].text
                            if get_title:
                                title = get_title[0]
                                
                        song_rating=get_rating(id3)
                        Music_Song.objects.create(song_artist=song_artist, 
                                                  song_genre=song_genre, 
                                                  album=album, 
                                                  filename=safe_song, 
                                                  type=safe_song.rsplit('.')[-1],
                                                  path=str(file_object),
                                                  title=title,
                                                  length=str(result),
                                                  letter=letter,
                                                  rating=song_rating,
                                                  file_size=str(file_size)
                                                  )
                        song_count += 1
                album.length = time.strftime('%M:%S', time.gmtime(album_length))
                album.song_count = song_count
                album.album_size = str(album_size)
                if album_genres: album.album_genre = max(album_genres, key=album_genres.get)
                
                if album_year: 
                    string_album_year = album_year.encode('ascii','ignore')
                    if string_album_year: album.year = int(string_album_year[0]+string_album_year[1]+string_album_year[2]+string_album_year[3])
                    if album.year < 1800 or album.year > 2020:
                        album.year = 0
                else: album.year = 0
                album.save()
    return #render_to_response('confirmation.html', locals())
 
def update_album_art(request):
    letter_list = LETTERS
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

def filter_nzbs(request):
    path_to_nzbs = 'D:/QmA/NZB/Music/Albums/Download/new/ready/'
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
    
    for albums in albums_in_DB:
        counter += 1
        for nzbs in all_nzbs:
            if albums.folder == nzbs.rsplit('.NZB')[0]:
                #print 'Found Match: \n', albums.folder, '\n',  nzbs.rsplit('.NZB')[0]
                try:
                    os.rename(path_to_nzbs+nzbs, path_to_nzbs+'exact_duplicate/'+nzbs)
                except:
                    print 'Failed to move the duplicate file.'
            else:
#                try:
#                    safe = albums.folder[15]
#                    if safe:
#                        if albums.folder in nzbs.rsplit('.NZB')[0]:
#                            try:
#                                os.rename(path_to_nzbs+nzbs, path_to_nzbs+'partial_duplicate/'+nzbs)
#                            except:
#                                print 'Failed to move the duplicate file.'
#                except:
#                    pass#print albums.folder, 'was not safe\n'

                #More aggressive elimination of albums
                try:
                    name = albums.artist.artist.replace(' ','.')+'-'+albums.album.replace(' ','.')
                    safe = name[14]
                    if name in nzbs.rsplit('.NZB')[0]:
                        try:
                            os.rename(path_to_nzbs+nzbs, path_to_nzbs+'partial_duplicate/'+nzbs)
                            print '----------------------found----------------------------'
                        except:
                            print 'Failed to move the duplicate file.', nzbs
                except:
                    #print name
                    pass#print albums.folder, 'was not safe\n'
                                
        if counter % 1000 == 0:
            print counter
    return HttpResponseRedirect('/')

def rename_nzbs(request):
    message = ''
#    for letter in LETTERS:
#        print 'processing '+ 'L:/media/static/music/'+letter+'/'
#        path_to_nzbs = 'L:/media/static/music/'+letter+'/'
    path_to_nzbs = 'D:/QmA/NZB/Music/Albums/Download/new/ready/'
    os.chdir(path_to_nzbs)
    all_nzbs = os.listdir('.')
    try:
        os.makedirs('failed')
    except:
        print 'Failed to create the failed directory\n'        
    
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
        string2 = string2.replace('Z-RO', 'Z.RO')
        string2 = string2.replace('Q-TIP', 'Q.TIP')
        string2 = string2.replace('NE-YO', 'NE.YO')
        string2 = string2.replace('AC-DC', 'ACDC')
        string2 = string2.replace('AC.DC', 'ACDC')
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
        if string2[0] == '.':
            string2 = string2.lstrip('.')
        if string[0] == '-':
            string2 = string2.lstrip('-')
            
        if string != string2:
            try:
                message += 'Renaming ' + nzbs + ' to ' + string2 + '<br/>' 
                win32file.MoveFile(path_to_nzbs+nzbs, path_to_nzbs+string2)
                #os.rename(path_to_nzbs+nzbs, path_to_nzbs+string2)
                #print 'Renaming of ', nzbs , ' to \n', string2, ' completed' 
            except:
                print 'Renaming of ', nzbs , ' to \n', string2, ' failed' 
                try:
                    win32file.MoveFile(path_to_nzbs+nzbs, path_to_nzbs+'failed/'+string2)
                except:
                    print 'Moving a file that failed to rename also Failed. WOW.'
    
    return render_to_response('confirmation.html', locals())
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
        
    #return render_to_response('base.html', locals())

@login_required
def albums(request, letter):
    all_albums_full = Music_Album.objects.all().order_by('album')
    all_albums = []
    if letter == "all":
        all_albums = all_albums_full
    else:
        all_albums = []
        for all_album_full in all_albums_full:
            added = False
            try: 
                if all_album_full.album[0] == letter and letter != 'T':
                    added = True
                    all_albums.append(all_album_full) 
                elif all_album_full.album[0] == 'T' and letter == 'T':
                    added = True
                    if all_album_full.album[1] != 'H':
                        all_albums.append(all_album_full)
                elif all_album_full.album[0] == 'T':
                    added = True
                    if all_album_full.album[1] == 'H' and all_album_full.album[2] == 'E' and all_album_full.album[4] == letter :
                        all_albums.append(all_album_full)
                elif letter == '0' and added == False:
                    print all_album_full.album, '\n'
                    all_albums.append(all_album_full)
#                else:
#                    all_albums.append(all_album_full)
            except:
                pass
            
            if not (request.user.is_superuser or request.user.is_staff) and len(all_albums) >= GUEST_ACCESS:
                break
            
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
        all_albums = Music_Album.objects.filter(album_artist=artist).order_by('album')[:GUEST_ACCESS]
        
    if request.is_ajax():
        mimetype = 'application/javascript'
        albums = simplejson.dumps(albums_by_requirement(all_albums))
    return HttpResponse(albums, mimetype)


@login_required
def albums_by_year(request, year_id):
    if request.user.is_superuser or request.user.is_staff:
        all_albums = Music_Album.objects.filter(year=year_id).order_by('album')
    else:
        all_albums = Music_Album.objects.filter(year=year_id).order_by('album')[:GUEST_ACCESS]    
        
    if request.is_ajax():
        mimetype = 'application/javascript'
        albums = simplejson.dumps(albums_by_requirement(all_albums))
    return HttpResponse(albums, mimetype)


@login_required
def albums_by_genre(request, genre_id):
    if request.user.is_superuser or request.user.is_staff:
        all_albums = Music_Album.objects.filter(album_genre=genre_id).order_by('album')
    else:
        all_albums = Music_Album.objects.filter(album_genre=genre_id).order_by('album')[:GUEST_ACCESS]    
        
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
    if request.user.is_superuser or request.user.is_staff:
        if letter == 'all': get_artists = Music_Artist.objects.all().order_by('artist')
        else: get_artists = Music_Artist.objects.filter(letter=letter).order_by('artist')
    else:
        if letter == 'all': get_artists = Music_Artist.objects.all().order_by('artist')[:GUEST_ACCESS]
        else: get_artists = Music_Artist.objects.filter(letter=letter).order_by('artist')[:GUEST_ACCESS]
        
    artists = []
    for get_artist in get_artists:
        try:
            artist = {}
            artist['pk'] = get_artist.id
            artist['name'] = get_artist.artist
            artist['song_count'] = 0
            artist['album_count'] = 0
            artist['albums'] = []
            get_albums = Music_Album.objects.filter(album_artist=get_artist.id).order_by('id')
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
    all_artists = Music_Album.objects.all()
    get_artists = []
    for items in all_artists:
        if request.GET['query'].upper() in items.album_artist.artist.upper():
            if items.album_artist not in get_artists:
                get_artists.append(items.album_artist)
            
    artists = []
    for get_artist in get_artists:
        try:
            artist = {}
            artist['pk'] = get_artist.id
            artist['name'] = get_artist.artist
            artist['song_count'] = 0
            artist['album_count'] = 0
            artist['albums'] = []
            get_albums = Music_Album.objects.filter(album_artist=get_artist.id).order_by('id')
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
    return HttpResponse(artists, mimetype)
    
        
@login_required
def search_music_albums(request):
    
    get_albums = Music_Album.objects.all()
    all_albums = []
    for items in get_albums:
        if request.GET['query'].upper() in items.album.upper():
            all_albums.append(items)
                        
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
def search_music_songs(request):
    
    get_songs = Music_Song.objects.all()
    all_songs = []
    for items in get_songs:
        if items.title:
            if request.GET['query'].upper() in items.title.upper():
                all_songs.append(items)
                      
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
    return HttpResponse(albums, mimetype)


def upload_music(request):
    theme = 'theme_white'
    letter_list = LETTERS
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
        destination = open('L:/media/static/music/UPLOADS/'+file[key].name, 'wb+')
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
    
    
    
    
    
    
    
    
    
    
    
    
    