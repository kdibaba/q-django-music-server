from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.core import serializers

from media.music.forms import *
from media.music.models import *

import os, sys, shutil, win32file, re, time

from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

def music(request):
    return render_to_response('base.html', locals)

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
        if request.POST['drive']:
            directory = str(request.POST['drive']) + '/' 
            file_list = get_folder_names(directory)
            if 'catalog_drive' in request.POST:
                cataloged, problems = catalog_drive_music (file_list, request.POST['drive_name'], directory)
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

def catalog_drive_music (files, drive, directory):
    cataloged = []
    problems = []
    
    #Delete all records for this drive
    #Music_Drive.objects.filter(drive=drive).delete()
    
    #Save the drive data
    #drive = Music_Drive.objects.create(drive=drive)
    
    for file_object in files:
        file = str(file_object).split('-')
        if file.__len__() > 1:
            cataloged.append(str(file_object))
            songs = os.listdir(directory+str(file_object))
            artist_name = file[0].replace('.', ' ')
            artist = Music_Artist.objects.filter(artist=artist_name)
            if not artist:
                artist = Music_Artist.objects.create(artist=artist_name)
            else: artist = artist[0]
            album_name = file[1]
            album_art = True
            if 'Folder.jpg' not in songs:
                album_art=False
            
            album = Music_Album.objects.create(artist=artist, album=album_name, folder=str(file_object), album_art=album_art)
            id3_info = {}
            for song in songs:
                if song.rsplit('.')[-1] == 'mp3':
                    id3 = EasyID3(directory+str(file_object)+'/'+song)
                    property = MP3(directory+str(file_object)+'/'+song)
                    result = time.strftime('%M:%S', time.gmtime(property.info.length))
                    Music_Song.objects.create(artist=artist, 
                                              album=album, 
                                              filename=song, 
                                              type=song.rsplit('.')[-1],
                                              path='A/'+str(file_object),
                                              title=id3['title'][0],
                                              length=str(result)
                                              )            
            
        else:
            problems.append(str(file_object))
        
    return cataloged, problems

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

def albums(request):
    albums = ''
    if request.is_ajax():
        mimetype = 'application/javascript'
        albums = serializers.serialize('json', Music_Album.objects.all())
    return HttpResponse(albums, mimetype)

def album_info(request, album_id):
    albuminfo = ''
    print album_id
    album = Music_Album.objects.get(id=album_id)
    print album
    if request.is_ajax():
        mimetype = 'application/javascript'
        albuminfo = serializers.serialize('json', Music_Album.objects.filter(id=album_id))
    return HttpResponse(albuminfo, mimetype)

def album(request, album_id):
    album = Music_Album.objects.get(id=album_id)
    songs = ''
    if request.is_ajax():
        mimetype = 'application/javascript'
        songs = serializers.serialize('json', Music_Song.objects.filter(album=album, type="mp3"))
    return HttpResponse(songs, mimetype)

def albums_by_artist(request, artist_id):
    artist = Music_Artist.objects.get(id=artist_id)
    albums = ''
    if request.is_ajax():
        mimetype = 'application/javascript'
        albums = serializers.serialize('json', Music_Album.objects.filter(artist=artist))
    return HttpResponse(albums, mimetype)

def artists(request):
    artists = ''
    if request.is_ajax():
        mimetype = 'application/javascript'
        artists = serializers.serialize('json', Music_Artist.objects.all())
    return HttpResponse(artists, mimetype)
    
    
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
    
        