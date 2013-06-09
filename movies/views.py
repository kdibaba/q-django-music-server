from django.shortcuts import render_to_response
from media.movies.forms import *
from media.movies.models import *

import os, sys, shutil, win32file, re

IGNORE_FILES    = ['ehthumbs_vista.db', '$recycle.bin', 'system volume information']
NZB_LOCATION    = 'c:/qma/nzb/hd movies/download/'
HYPHENATE       = ['720p','hdtv','bluray','unrated','directors.cut',
                   'repack','x264','hddvd', 'dvd5', 'dvd9', 'dts',
                   'readnfo', 'proper', 'oar', '2audio', 'ac3', '1080p',
                   'divx','xvid','dvdrip','dvd','r5', 'internal', 'se', 'dc','limited']

def handle_movies_drive(request):
    msg = ''
    directory = ''
    directories = []
    string_file_list = []
    copies = []
    num_of_copies = 0
    partial_copies = []
    moved_files = []
    num_of_partial_copies = 0
    renamed_files = []
    file_list = []
    cataloged = []
    problems = []
    
    if request.method == 'POST':
        form = Drive_form(request.POST)
        if request.POST['drive']:
            directory = str(request.POST['drive'])
            file_list = get_file_names(directory)
            if 'catalog_drive' in request.POST:
                if request.POST['drive_name']:
                    cataloged, problems = catalog_drive_movies(directory, file_list, request.POST['drive_name'])
                else: problems.append('You forgot to put in a drive name!')
            elif 'rename_files_simple' in request.POST:
                renamed_files, problems = rename_files_simple(directory)
            # elif 'rename_files_complex' in request.POST:
            #     if request.POST['drive_name']:
            #         renamed_files, problems = rename_files_complex (file_list, directory, request.POST['drive_name'])
            #     else: problems.append('You forgot to put in a drive name!')
            elif 'move_files' in request.POST:
                moved_files, problems = move_files(file_list, directory)
            file_list = get_file_names(directory)
        else: problems.append('You forgot to put in a drive location!')       
            
        if 'check_nzbs' in request.POST:
            if request.POST['nzbs']:
                nzbs = str(request.POST['nzbs'])
                copies, num_of_copies, problems, partial_copies, num_of_partial_copies = handle_nzbs (nzbs)
            else: problems.append('You forgot to put in the complete path to the nzb folder name')
         
    else:
        form = Drive_form()
    return render_to_response('handle_movies_drive.html', { 'form'                  : form, 
                                                            'cataloged'             : cataloged,
                                                            'renamed_files'         : renamed_files,
                                                            'file_list'             : file_list,
                                                            'problems'              : problems,
                                                            'copies'                : copies,
                                                            'num_of_copies'         : num_of_copies,
                                                            'partial_copies'        : partial_copies,
                                                            'num_of_partial_copies' : num_of_partial_copies,
                                                            'moved_files'           : moved_files,
                                                            'msg'                   : msg, } )    
    
    
def handle_nzbs (nzbs_path):
    nzbs = os.listdir(nzbs_path) 
    try: os.makedirs(nzbs_path+'/Exact Match/')
    except: pass
    try: os.makedirs(nzbs_path+'/Partial Match/')
    except: pass   
    copies = [] 
    partial_copies = []
    num_of_copies = 0
    num_of_partial_copies = 0
    all_movies = Movie_Name.objects.all()
    file_names = []
    movie_names = []
    problems = []
    for movie in all_movies:
        file_names.append(movie.file_name.replace('.mkv', '.nzb').lower())
        movie_names.append(movie.movie_name.replace(' ', '.').lower())
    
    # Get Pending HD NZBS
    for root, dirs, files in os.walk('C:/QmA/NZB/HD Movies/download/'):
        for name in files:
            movie_names.append(str(name).lower().split('-')[0])
        
    for nzb in nzbs:
        if str(nzb).lower() in file_names:
            copies.append(nzb)
            num_of_copies += 1
            try:
                win32file.MoveFile(nzbs_path+'/'+nzb, nzbs_path+'/Exact Match/'+nzb)
            except:
                problems.append(nzbs_path+nzb)
        #elif str(nzb).lower().split('-')[0] in movie_names:
        else:
            for movies in movie_names:
                if str(nzb).lower().split('-')[0] == movies:
                    partial_copies.append(nzb +'<br />'+movies.upper()+'<br />')
                    num_of_partial_copies += 1
                    try:
                        win32file.MoveFile(nzbs_path+'/'+nzb, nzbs_path+'/Partial Match/'+nzb)
                    except:
                        problems.append(nzbs_path+nzb)
                    break
    return copies, num_of_copies, problems, partial_copies, num_of_partial_copies
    
def get_file_names (directory):
    
    file_list = os.listdir(directory)
    
    return file_list

def move_files (files, directory):
    moved_files = []
    problems = []

    for file in files:
        if os.path.isdir(directory+str(file)) == False:
            if '.MKV' in str(file) or '.AVI':
                new_directory = str(file).replace('.MKV', '').replace('.AVI', '')
                try: 
                    os.mkdir(directory+new_directory)
                except: problems.append('Not Exactly a Problem - Unable to make New Directory - '+str(file))
                try:
                    win32file.MoveFile(directory+str(file), directory+new_directory+'/'+str(file))
                    moved_files.append(str(file))
                except: problems.append('Unable to move file - ' + str(file))
        elif str(file) != 'System Volume Information' and str(file) != '$RECYCLE.BIN':
            folder_contains = os.listdir(directory+str(file))
            if not folder_contains:
                print 'Folder is empty: ', str(file)
            else:
                for movie_file in folder_contains:
                    if '.mkv' in str(movie_file).lower() or '.avi' in str(movie_file).lower():
                        if str(file) != str(movie_file).split('-')[0].replace('.',' '):
                            try: win32file.MoveFile(directory+str(file), directory+str(movie_file).replace('.',' ').split('-')[0])
                            except: problems.append('Duplicate files: '+ str(file))
                            break


            
    return moved_files  , problems

def rename_files_simple (directory):
    renamed_files = {}
    counter = 0
    problems = []
    files = os.listdir(directory)
    for file in files: 
        # Make sure to ignore system files 
        ignore = False 
        if str(file) != 'System Volume Information' and str(file) != '$RECYCLE.BIN':
            try: folder_contains = os.listdir(directory+str(file))
            except: break
            if not folder_contains:
                print 'Folder is empty: ', str(file)
            else:
                for movie_file in folder_contains:
                    if '.mkv' in str(movie_file).lower() or \
                    '.avi' in str(movie_file).lower() or \
                    '-mkv' in str(movie_file).lower() or \
                    '-avi' in str(movie_file).lower():
                        string = str(movie_file)

                        for item in IGNORE_FILES:
                            if item in string.lower():
                                ignore = True 
                                
                        if not ignore:
                            string2 = string.lower()
                            string2 = string2.replace(' ', '.')
                            string2 = string2.replace('_', '.')
                            string2 = string2.replace('[', '.')
                            string2 = string2.replace(']', '.')
                            string2 = string2.replace('(', '.')
                            string2 = string2.replace(')', '.')
                            string2 = surround_with_hyphen( string2 )
                            string2 = string2.replace('blu-ray', '-bluray-')
                            string2 = string2.replace('blu.ray', '-bluray-')
                            string2 = string2.replace('.bdrip.', '-bluray-')
                            string2 = string2.replace('.bd-rip.', '-bluray-')
                            string2 = string2.replace('.hddvdrip.', '-hddvd-')
                            string2 = string2.replace('-hddvd-rip-', '-hddvd-')
                            string2 = string2.replace('.hd-dvd.', '-hddvd-')
                            string2 = string2.replace('.hd.dvd.', '-hddvd-')
                            string2 = string2.replace('hd.dvd', '-hddvd-')
                            string2 = string2.replace('.nzb.nzb', '.nzb')
                            string2 = string2.replace('&quot', '.')
                            string2 = string2.replace('par2', '.')
                            string2 = string2.replace('rar', '.')
                            string2 = string2.replace('.-', '-')
                            string2 = string2.replace('-.', '-')
                            string2 = string2.replace('--', '-')
                            string2 = string2.replace('--', '-')
                            string2 = string2.replace('--', '-')
                            string2 = string2.replace('..', '.')
                            string2 = string2.replace('..', '.')
                            #string2 = string2.replace('\'', '.')
                            string2 = string2.replace(',', '.')
                            string2 = string2.replace('{', '.')
                            string2 = string2.replace('}', '.')
                            string2 = string2.replace('-nzb', '.nzb')
                            string2 = string2.replace('-rar', '.rar')
                            string2 = string2.replace('-mkv', '.mkv')
                            string2 = string2.replace('-avi', '.avi')
                            string2 = string2.upper()
                            if string2[-1] == '-':
                                string2 = string2.rsplit('-', 1)[0]
                            if string2[0] == '.':
                                string2 = string2.split('.', 1)[1]
                            if string2[0] == '-':
                                string2 = string2.split('-', 1)[1]
                                
                            if string != string2 and 'RECYCLE' not in string:
                                counter += 1
                                renamed_files[string] = string2
                                try:
                                    win32file.MoveFile(directory+str(file)+'/'+string, directory+str(file)+'/'+string2)
                                except:
                                    for file in files:
                                        if string2 == str(file):
                                            problems.append('File exists so it cant be renamed.')
                                            #win32file.DeleteFile(directory+string)
                                    problems.append(str(counter)+' '+directory+str(string2))
    #print counter        
    return renamed_files, problems
    
def surround_with_hyphen (file):
    match_year_numbers = '[0-9][0-9][0-9][0-9]'
    match_year_numbers_ignore_2 = '[0-9][0-9][0-9][0-9][0-9]'
    match_year_numbers_ignore = '\-[0-9][0-9][0-9][0-9]\-'
    
    string = str(file)
    match  = re.search(match_year_numbers, string)
    match2  = re.search(match_year_numbers_ignore, string)
    match3  = re.search(match_year_numbers_ignore_2, string)
    string2 = string
    if match and not match2 and not match3:
        match = match.group()
        file = string2.replace(match, '-'+match+'-')
          
    for item in HYPHENATE:
        file = file.replace('.'+item+'.', '-'+item+'-')
        file = file.replace('.'+item+'-', '-'+item+'-')
        file = file.replace('-'+item+'.', '-'+item+'-')
    return file
    
# def rename_files_complex (files, directory, drive_type):
    # renamed_files = {}
    # problems = []
    # counter = 0
    # counter_match_year = 0
    # match_year_numbers = '[0-9][0-9][0-9][0-9]'
    # match_year_numbers_ignore_2 = '[0-9][0-9][0-9][0-9][0-9]'
    # match_year_numbers_ignore = '\-[0-9][0-9][0-9][0-9]\-'
    # for file in files:
    #     # Make sure to ignore system files 
    #     ignore = False 
    #     string = str(file)
    #     for item in IGNORE_FILES:
    #         if item in string.lower():
    #             ignore = True 
                
    #     if not ignore:                
    #         string = str(file)
    #         match  = re.search(match_year_numbers, string)
    #         match2  = re.search(match_year_numbers_ignore, string)
    #         match3  = re.search(match_year_numbers_ignore_2, string)
    #         string2 = string
    #         if match and not match2 and not match3:
    #             match = match.group()
    #             string2 = string2.replace(match, '-'+match+'-')
    #             counter_match_year += 1
                
    #         if string != string2:
    #             counter += 1
    #             renamed_files[string] = string2
    #             try:
    #                 win32file.MoveFile(directory+string, directory+string2)
    #             except:
    #                 problems.append(str(counter)+' '+directory+str(string2)) 
    
    #now rename files inside the folders
    
    # for file in files:
    #     # Make sure to ignore system files
    #     ignore = False 
    #     string = str(file)
    #     for item in IGNORE_FILES:
    #         if item in string.lower():
    #             ignore = True 
                
    #     if not ignore:
    #         if 'HD.Movies' in drive_type:
    #             counter += 1
    #             if os.path.isdir(directory+str(file)) == True :
    #                 file_list = os.listdir(directory+str(file))
    #                 mkv_counter = 0
    #                 mkv_file = ''
    #                 for items in file_list:
    #                     if '.mkv' in items.lower():
    #                         mkv_counter += 1
    #                         mkv_file = items
                    
    #                 if mkv_counter == 1:
    #                     try:
    #                         win32file.MoveFile(str(directory+str(file)+'/'+str(mkv_file)), str(directory+str(file)+'/'+str(file)+'.mkv'))
    #                         renamed_files[directory+str(file)+'/'+str(mkv_file)] = str(directory+str(file)+'/'+str(file)+'.mkv')
    #                     except:
    #                         problems.append(str(counter)+' '+file)
    #                 else:
    #                     problems.append(str(counter)+' '+file)
    #             else: pass
    #                 #This code will help if there are movies that are not in folders!
    #                 #try: os.makedirs(str(directory)+'/'+str(file).rsplit('.', 1)[0])
    #                 #except: print str(file), ' failed'
    #         elif 'Movies' in drive_type:
    #             if os.path.isdir(directory+str(file)) == True :
    #                 file_list = os.listdir(directory+str(file))
    #                 avi_counter = 0
    #                 avi_file = []
    #                 for items in file_list:
    #                     if '.avi' in items.lower():
    #                         avi_counter += 1
    #                         avi_file.append(items)
                    
    #                 if avi_counter == 1:
    #                     if str(directory+str(file)+'/'+str(avi_file[0])) != str(directory+str(file)+'/'+str(file)+'.avi'):
    #                         try:
    #                             win32file.MoveFile(str(directory+str(file)+'/'+str(avi_file[0])), str(directory+str(file)+'/'+str(file)+'.avi'))
    #                             renamed_files[directory+str(file)+'/'+str(avi_file[0])] = str(directory+str(file)+'/'+str(file)+'.avi')
    #                         except:
    #                             counter += 1
    #                             problems.append(str(counter)+' '+file)
    #                 elif avi_counter == 2:
    #                     try:
    #                         win32file.MoveFile(str(directory+str(file)+'/'+str(avi_file[0])), str(directory+str(file)+'/'+str(file)+'.CD1.avi'))
    #                         renamed_files[str(avi_file[0])] = str(file)+'.CD1.avi'
    #                         win32file.MoveFile(str(directory+str(file)+'/'+str(avi_file[1])), str(directory+str(file)+'/'+str(file)+'.CD2.avi'))
    #                         renamed_files[str(avi_file[1])] = str(file)+'.CD2.avi'
    #                     except:
    #                         counter += 1
    #                         problems.append(str(counter)+' '+file)                                
    #                 else:
    #                     counter += 1
    #                     problems.append(str(counter)+' '+file)
    #             else: pass
    #                 #This code will help if there are movies that are not in folders!
    #                 #try: os.makedirs(str(directory)+'/'+str(file).rsplit('.', 1)[0])
    #                 #except: print str(file), ' failed'
    # problems.append( '\nAll Counter is ' + str(counter))
    # problems.append( 'counter_match_year Counter is ' + str(counter_match_year))  
                
    
    return renamed_files, problems

def catalog_drive_movies (directory, files, drive_name):
    cataloged = []
    problems = []
    
    #Delete all records for this drive
    Movie_Drive.objects.filter(drive=drive_name).delete()
    #Save the drive data
    drive_info = win32file.GetDiskFreeSpaceEx(directory)
    drive = Movie_Drive.objects.create(drive=drive_name, drive_capacity=int(drive_info[1]) , drive_free_space=int(drive_info[0]))
    
    for file_object in files:
        if file_object.lower() not in IGNORE_FILES and file_object != "0":
            path = directory+str(file_object)
            movie_name = ""
            if os.path.isdir(path) != True:
                file = str(file_object).split('-')
                if file.__len__() > 1:
                    movie_name = str(file[0])
                else:
                    movie_name = str(files).rsplit('.', 1)[0]
                file_size=str(os.path.getsize(file_object))
                file_name=str(file_object)
            else:
                try:
                    file_list = os.listdir(path)
                    for files in file_list:
                        if 'HD.Movies' in drive_name:
                            if ".mkv" in files or '.MKV' in files:
                                file = str(files).split('-')
                                if file.__len__() > 1:
                                    movie_name = str(file[0])
                                else:
                                    movie_name = str(files).rsplit('.', 1)[0]
                                file_size=str(os.path.getsize(path + '/' + files))
                                file_name=str(files)
                                break
                        elif 'Movies' in drive_name:
                            if ".avi" in files or '.AVI' in files:
                                file = str(files).split('-')
                                if file.__len__() > 1:
                                    movie_name = str(file[0])
                                else:
                                    movie_name = str(files).rsplit('.', 1)[0]
                                file_size=str(os.path.getsize(path + '/' + files))
                                file_name=str(files)
                                break
                                
                except:
                    pass
            
            if movie_name != "":
                Movie_Name.objects.create(drive=drive, movie_name=movie_name.replace('.', ' '),  
                                          file_name=file_name, file_size=file_size)
                cataloged.append(str(file_object))
            else:
                problems.append(str(file_object))
        
    return cataloged, problems


def view_movies(request):
    msg = ''
    movies = {}
    drives = {}
    form = {}
    # Movie_Drive.objects.filter(drive='HD.Movies.007').delete()
    drives = Movie_Drive.objects.all().order_by('drive')
    
    if request.method == 'POST':        
        for drive in drives:
            if drive.drive in request.POST:
                movies = Movie_Name.objects.filter(drive=drive).order_by('movie_name')
                
    all_movies = Movie_Name.objects.all().order_by('movie_name')
    return render_to_response('view_movies.html', { 'drives' : drives,
                                                    'movies' : movies,
                                                    'all_movies' : all_movies,
                                                    'msg'    : msg, } )

    
def search_movies(request):
    results = []
    num_of_results = 0
    search = ''
    if request.method == 'POST':
        if request.POST['search']:
            search = request.POST['search'].lower()
            movies = Movie_Name.objects.all().order_by('movie_name')
            for movie in movies:
                if search in movie.movie_name.lower():
                    results.append( movie )
            num_of_results = results.__len__()
        
    return render_to_response('search_movies.html', {  'results'         : results,
                                                      'num_of_results'  : num_of_results,
                                                      'search'          : search})
    