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


LETTERS = ['0', 'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
SET_RATING = {'1': 32, '2': 64, '3': 128,'4':196, '5':255}

@login_required
def music(request):
    letter_list = LETTERS
    return render_to_response('base.html', locals())

@login_required
def add_to_music_db(request):
    result = 0    
    if request.is_ajax():
        mimetype = 'application/javascript'
        catalog_drive_music('add')
        result = 1
    return HttpResponse(result, mimetype)
    
@login_required
def rebuild_music_db(request):
    result = 0        
    if request.is_ajax():
        mimetype = 'application/javascript'
        catalog_drive_music('rebuild')
        result = 1
    return HttpResponse(result, mimetype)
        
def handle_music_drive(request):
    msg = ''
    directory = ''
    directories = []
    string_file_list = []
    copies = []
    renamed_files = []
    file_list = []
    cataloged = []
    problems = []
    num_of_copies = 0
    duplicates = []
    if request.method == 'POST':
        form = Drive_form(request.POST)
        if 'catalog_drive' in request.POST:
            cataloged, problems = catalog_drive_music ()
        elif 'filter_nzbs' in request.POST:
            if request.POST['nzbs']:
                num_of_copies, copies  = filter_nzbs_music (file_list, request.POST['nzbs'])
            else: problems.append('You forgot to give me the location of the nzbs!')
        elif 'fix_albums' in request.POST:
            if request.POST['directory']:
                duplicates  = fix_albums (request.POST['directory'])
            else: problems.append('You forgot to give me the location of the nzbs!')
                
    else:
        form = Drive_form()
    return render_to_response('handle_music_drive.html', {  'form'              : form, 
                                                            'cataloged'         : cataloged,
                                                            'file_list'         : file_list,
                                                            'problems'          : problems,
                                                            'copies'            : copies,
                                                            'num_of_copies'     : num_of_copies,
                                                            'duplicates'        : duplicates,
                                                            'msg'               : msg, } )    
    
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
    for letter in LETTERS: 
        directory = settings.MUSIC_DIRECTORY + letter + "/"
        files = get_folder_names(directory)
        cataloged = []
        problems = []
        
        #Delete all records for this drive
        #Music_Drive.objects.filter(drive=drive).delete()
        
        #Save the drive data
        #drive = Music_Drive.objects.create(drive=drive)
        
        for file_object in files:
            try:
                file = str(file_object).split('-')
                album_exists = Music_Album.objects.filter(folder=str(file_object))
                if file.__len__() > 1 and not album_exists:
                    album_length = 0
                    album_year = 0
                    album_size = 0
                    cataloged.append(str(file_object))
                    try: songs = os.listdir(directory+str(file_object))
                    except: songs = []
                    artist_name = file[0].replace('.', ' ')
                    artist = Music_Artist.objects.filter(artist=artist_name)
                    if not artist:
                        artist = Music_Artist.objects.create(artist=artist_name)
                    else: artist = artist[0]
                    album_name = file[1].replace('.', ' ')
                    album_art = True
                    if 'Folder.jpg' not in songs:
                        album_art=False
                    
                    album = Music_Album.objects.create(artist=artist, album=album_name, folder=str(file_object), album_art=album_art, letter=letter)
                    artist.letter = letter
                    artist.save()
                    id3_info = {}
                    song_count = 0
                    for song in songs:
                        #print file, ' ----- ', song
                        if song.rsplit('.')[-1] == 'mp3':
                            song_length = 0
                            song_rating = 0
                            file_size = ''
                            try:
                                id3 = ID3(directory+str(file_object)+'/'+song)
                                property = MP3(directory+str(file_object)+'/'+song)
                                song_length = property.info.length
                                album_length += song_length
                                result = time.strftime('%M:%S', time.gmtime(song_length))
                                #print directory+str(file_object)+'/'+song
                                file_size=os.path.getsize(directory+str(file_object)+'/'+song)
                                album_size += file_size
                                title=''
                                try:title=id3.getall('TIT2')[0].text[0]
                                except:title=filename
                                if not album_year:
                                    try:album_year=id3.getall('TDRC')[0].text[0]
                                    except:pass
                                try:song_rating=get_rating(id3.getall('POPM')[0].rating)
                                except:pass
                                Music_Song.objects.create(artist=artist, 
                                                          album=album, 
                                                          filename=song, 
                                                          type=song.rsplit('.')[-1],
                                                          path=str(file_object),
                                                          title=title,
                                                          length=str(result),
                                                          letter=letter,
                                                          rating=song_rating,
                                                          file_size=str(file_size)
                                                          )
                                song_count += 1
                            except:
                                print str(file_object)
                    album.length = time.strftime('%M:%S', time.gmtime(album_length))
                    album.song_count = song_count
                    album.album_size = str(album_size)
                    if album_year: 
                        string_album_year = album_year.encode('ascii','ignore')
                        try: 
                            album.year = int(string_album_year[0]+string_album_year[1]+string_album_year[2]+string_album_year[3])
                            if album.year < 1800 or album.year > 2020:
                                album.year = 0
                        except: album.year = 0
                    else: album.year = 0
                    album.save()
                    
                else:
                    problems.append(str(file_object))
                    print "skipping " +str(file_object)
            except:
                print 'Excepted on ' + file_object
    return cataloged, problems

def get_rating(rating):
    if rating == 255:
        return 5
    elif rating < 255 and rating >=196:
        return 4
    elif rating < 196 and rating >=128:
        return 3
    return 0

def filter_nzbs_music (files, nzb_location):
    
    os.chdir(nzb_location)
    try:
        os.makedirs(nzb_location+'duplicate')
    except:
        pass
    all_nzbs = os.listdir('.')
    counter = 0
    progress_counter = 0
    copies = []
    string2 = ''
    all_albums = Music_Album.objects.all()
    all_folders = []
    for album in all_albums:
        all_folders.append(str(album.folder))
        #all_folders.append(str(album.artist.artist)+'-'+str(album.album))
    
    #all_albums = os.listdir('C:\QmA\NZB\Music\Albums\Collection')
    #for album in all_albums:
        #all_folders.append(str(album).replace('.nzb', ''))    
    
    remove = ['-CDS-','.CDS.','-PROMO-','.CDS.','BOOTLEG','(CDS)','(BOOTLEG)']
    for nzbs in all_nzbs:
        string = str(nzbs)
        string2 = string.replace('[', '.')
        string2 = string2.replace(']', '.')
        string2 = string2.replace('.NZB.nzb', '.nzb')
        string2 = string2.replace('..', '.')
        string2 = string2.replace('..', '.')
        string2 = string2.replace('..', '.')
        if string != string2:
            try:
                print nzb_location+nzbs, ' renamed to ', nzb_location+string2
                os.rename(nzb_location+nzbs, nzb_location+string2)
            except:
                print "Renaming the nzb failed\n"
    
    for folders in all_folders:
        for nzbs in all_nzbs:
            progress_counter = progress_counter + 1
            if folders == str(nzbs).rsplit('.', 1)[0] or folders == str(nzbs).rsplit('.', 2)[0]:
                try:
                    os.rename(nzb_location+nzbs, nzb_location+'duplicate/'+nzbs)
                    copies.append(str(nzbs))
                    counter = counter + 1
                except: print nzbs, ' duplicate file failed for\n', nzb_location+nzbs
            else:
                for items in remove: 
                    if items in nzbs:
                        try:
                            os.rename(nzb_location+nzbs, nzb_location+'duplicate/'+nzbs)
                            copies.append(str(nzbs))
                            counter = counter + 1
                        except: print nzbs, ' duplicate remove failed\n', nzb_location+nzbs
            if progress_counter % 1000000 == 0:
                print 'progress at ', progress_counter
        
    return counter, copies

@login_required
def albums(request, letter):
    all_albums_full = Music_Album.objects.all().order_by('album')
    all_albums = []
    if letter == "all":
        all_albums = all_albums_full
    else:
        all_albums = []
        for all_album_full in all_albums_full:
            try: 
                if all_album_full.album[0] == letter and letter != 'T':
                    all_albums.append(all_album_full) 
                elif all_album_full.album[0] == 'T' and letter == 'T':
                    if all_album_full.album[1] != 'H':
                        all_albums.append(all_album_full)
                elif all_album_full.album[0] == 'T':
                    if all_album_full.album[1] == 'H' and all_album_full.album[2] == 'E' and all_album_full.album[4] == letter :
                        all_albums.append(all_album_full)
            except:
                pass 
    dictionary_albums = []
    for album in all_albums:
        album_info = {}
        album_info['artist'] = album.artist.artist
        album_info['artist_id'] = album.artist.id
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
    album['folder'] = original_album.folder 
    album['letter'] = original_album.letter 
    album['year'] = original_album.year 
    album['song_count'] = original_album.song_count 
    album['artist'] = original_album.artist.artist 
    album['artist_id'] = original_album.artist.id 
    album['album_art'] = original_album.album_art
    album['album_size'] = original_album.get_album_size()
    album['songs'] = []
    for song in songs:
        song_dict = {}
        song_dict['pk']  =  song.id
        song_dict['filename']  =  song.filename
        song_dict['length']  =  song.length
        song_dict['title']  =  song.title
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
def delete_album(request, album_id):
    album = Music_Album.objects.get(id=album_id)
    message = album.artist.id
    songs = Music_Song.objects.filter(album=album)
    shutil.move(settings.MUSIC_DIRECTORY+album.letter+'/'+album.folder, settings.MUSIC_DIRECTORY+'DELETED/')
    for song in songs:
        song.delete()
    album.delete()      
    if request.is_ajax():
        mimetype = 'application/javascript'
    return HttpResponse(message, mimetype)

@login_required
def get_song(request, song_id):
    original_song = Music_Song.objects.get(id=song_id)
    song = {}
    song['pk'] = original_song.id 
    song['full_path'] = "/static/music/"+original_song.letter+"/"+original_song.path+"/"+original_song.filename
    song['title'] = original_song.title 
    if request.is_ajax():
        mimetype = 'application/javascript'
    return HttpResponse(simplejson.dumps(song), mimetype)

@login_required
def albums_by_artist(request, artist_id):
    artist = Music_Artist.objects.get(id=artist_id)
    all_albums = Music_Album.objects.filter(artist=artist)
    dictionary_albums = []
    for album in all_albums:
        album_info = {}
        album_info['artist'] = album.artist.artist
        album_info['artist_id'] = album.artist.id
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
def albums_by_year(request, year_id):
    all_albums = Music_Album.objects.filter(year=year_id)
    dictionary_albums = []
    for album in all_albums:
        album_info = {}
        album_info['artist'] = album.artist.artist
        album_info['artist_id'] = album.artist.id
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
def artists(request, letter):
    if letter == 'all':
        get_artists = Music_Artist.objects.all().order_by('artist')
    else:
        get_artists = Music_Artist.objects.filter(letter=letter).order_by('artist')
    artists = []
    for get_artist in get_artists:
        try:
            artist = {}
            artist['pk'] = get_artist.id
            artist['name'] = get_artist.artist
            artist['song_count'] = 0
            artist['album_count'] = 0
            artist['albums'] = []
            get_albums = Music_Album.objects.filter(artist=get_artist.id).order_by('id')
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
def rebuild(request, letter):
    Music_Artist.objects.filter(letter=letter).delete()
    return catalog_drive_music('none')
    
@login_required
def set_rating(request, song_id, rating):
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
    if request.is_ajax():
        mimetype = 'application/javascript'
    return HttpResponse(mimetype)
    
@login_required    
def search_music(request):
    results = []
    num_of_results = 0
    search = ''
    if request.method == 'POST':
        if request.POST['search']:
            search = request.POST['search'].lower()
            artists = Music_Artist.objects.all().order_by('artist')
            for artist in artists:
                if search in artist.artist.lower():
                    results.append( artist )
            num_of_results = results.__len__()
        
    return render_to_response('search_music.html', {  'results'         : results,
                                                      'num_of_results'  : num_of_results,
                                                      'search'          : search})
    
        
        
def upload_music(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES)
            return HttpResponseRedirect('/')
    else:
        form = UploadFileForm()
    return render_to_response('upload.html', {'form': form})     

def handle_uploaded_file(file):
    print file
    return 