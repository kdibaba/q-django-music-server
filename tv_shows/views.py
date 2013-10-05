# Create your views here.
from django.shortcuts import render_to_response
from django.http import HttpResponse
from media.tv_shows.forms import *
from media.tv_shows.models import *
from django.contrib.auth.decorators import login_required

import os, sys, shutil, win32file, re


Seasons = ['S2000','S2001','S2002','S2003','S2004','S2005','S2006','S2007','S2008','S2009','S2010','S2011','S2012','S2013','S2014',
           'S00', 'S01','S02','S03','S04','S05','S06','S07','S08','S09', 'S10', 'S11', 'S12',
           'S13','S14','S15','S16','S17','S18','S19','S20','S21', 'S22', 'S23', 'S24',
           'S25','S26','S27','S28','S29','S30','S31', 'S32', 'S33', 'S34','S35','s36',
           'S37','S38','S39','S40','S41', 'S42', 'S43', 'S44','S45','S46','S47','S48'
           ]

QUALITIES = {
             'HiDEF'    :['720P', '1080P'],
             'HRHDTV'   :['HRHDTV', 'HR.HDTV'],
             'HRPDTV'   :['HRPDTV', 'HR.PDTV'],
             'DVD'      :['DVDRIP','DVD','DVDR'],
             'HDTV'     :['HDTV'],
             'PDTV'     :['PDTV'],
             'DIGITAL'  :['DSR'],
             'TV'       :['TVRIP'],
             'VCD'      :['VCD'],
             }

QUALITIES_VALUE = {
             'HiDEF'    :1,
             'HRHDTV'   :2,
             'HRPDTV'   :3,
             'DVD'      :4,
             'HDTV'     :5,
             'PDTV'     :6,
             'DIGITAL'  :7,
             'TV'       :8,
             'VCD'      :9,
             'UNKNOWN'  :10,
             }
VALID_FILE_TYPES = ['mkv', 'avi', 'mpg', 'm4a', 'ts', 'mp4']
EXCLUDE = ['ANIMANIACS']
IGNORE_FILES = ['ehthumbs_vista.db', 'recycle.bin', 'system volume information', 'desktop.ini', 'thumbs.db']


@login_required  
def index(request):
    return render_to_response('base.html')
    
@login_required    
def handle_tv_drive(request):
    msg = ''
    directory = ''
    directories = []
    string_file_list = []
    moved_files = []
    renamed_files = []
    file_list = []
    cataloged = []
    problems = [] 
    
    #check_existing_files()


    if request.method == 'POST':
        form = Drive_form(request.POST)
        if request.POST['drive_letter']:
            directory = str(request.POST['drive_letter'])
            if 'move_files' in request.POST:
                filenames, file_list = get_file_names(directory)
                moved_files, problems = move_files(filenames, directory)
                filenames, file_list = get_file_names(directory)
            elif 'catalog_drive' in request.POST:
                filenames, file_list = get_file_names(directory)
                if request.POST['drive']:
                    cataloged, problems = catalog_drive (file_list, request.POST['drive'], directory)
                else: problems.append('You forgot to put in a drive name!')
            elif 'rename_files_simple' in request.POST:
                renamed_files, problems = rename_files_simple(directory)
            elif 'rename_files_complex' in request.POST:
                renamed_files, problems = rename_files_complex (directory)
            elif 'cleanup_new_files' in request.POST:
                renamed_files, problems = cleanup_new_files(str(request.POST['drive_letter']))
            elif 'move_new_files' in request.POST:
                problems = move_new_files(str(request.POST['drive_letter']))
        if request.POST['nzbs']:
            if 'filter_nzbs' in request.POST:
                location = str(request.POST['nzbs'])
                moved_files, problems = filter_nzbs(location)
                
    else:
        form = Drive_form()
    return render_to_response('handle_tv_drive.html', { 'form'              : form, 
                                                        'cataloged'         : cataloged,
                                                        'file_list'         : file_list,
                                                        'moved_files'       : moved_files,
                                                        'problems'          : problems,
                                                        'renamed_files'     : renamed_files,
                                                        'string_file_list'  :string_file_list,
                                                        'msg'               : msg, } )


def filter_nzbs (directory):
    counter = 0
    found_counter = 0
    error_counter = 0
    os.chdir(directory)
    languages = ['german','french','dutch', 'danish', 'norwegian', 'swedish', 'flemish']
    folders = ['not_tv_show','inferior_quality','duplicate_2','duplicate', 'languages']
    for folder in folders:
        try:
            os.makedirs(directory+folder)
        except:
            pass
    all_nzbs = os.listdir('.')
    # all_episodes = TV_Shows.objects.all()
    moved_files = []
    problems = []
    for nzb in all_nzbs:
        counter += 1
        if counter % 100 == 0:
            print 'Completed ', str(counter), ' Files\n'
        
        done = False
        for language in languages:
            if language in str(nzb.lower()):
                win32file.MoveFile(directory + str(nzb), directory+'languages'+'/'+str(nzb))
                done = True
                break
        #If a foreign language is found in filename, get out of the for loop
        if done: continue

        if not is_tv_show(nzb) and not os.path.isdir(directory+str(nzb)):
            try:
                win32file.MoveFile(directory + str(nzb), directory+'not_tv_show'+'/'+str(nzb))
                error_counter += 1
                print str(error_counter) + ' Not a tv show', nzb
            except: 
                problems.append(directory + str(nzb))
                error_counter += 1
                print str(error_counter) + ' Problem Moving', nzb
            continue

        file = nzb.upper().rsplit('.NZB', 1)[0]

        file_quality = None
        episode = None
        episode2 = None
        season_object = None
        show_object = None
        found_season = False  
        found_quality = False
        for season_nums in Seasons:
            if season_nums in file and not found_season:
                found_season = True
                #Save the show data
                show_name = file.split(season_nums)[0]
                show_name = show_name.replace('.',' ')
                show_object = TV_Shows_Name.objects.filter(show=show_name)
                for shows in show_object:
                    if show_name == shows.show:
                        show_object = shows
                        break
                season = int(season_nums.replace('S', ''))
                episode_num = file.split(season_nums)[1]
                episode_num = episode_num.split('.')[0]
                try:
                    episode=int(episode_num[1]+episode_num[2])
                    try:
                        if episode_num[3] != 'E':
                            episode=int(episode_num[1]+episode_num[2]+episode_num[3])
                    except:
                        pass
                    try:
                        if episode_num[3] == 'E':
                            episode2 = int(episode_num[4]+episode_num[5])
                    except:
                        pass
                except:
                    episode=None
                break
                
        if show_object:
            search_tv_shows = TV_Shows.objects.filter(show=show_object, 
                                                      season__season=season,
                                                      episode=episode)
            for tv_show_found in search_tv_shows:
                if nzb.upper().rsplit('.NZB', 1)[0] == tv_show_found.file_name.upper().rsplit('.AVI', 1)[0].rsplit('.MKV', 1)[0]:
                    try:
                        found_counter += 1
                        win32file.MoveFile(directory + str(nzb), directory+'duplicate'+'/'+str(nzb))
                        moved_files.append(nzb.lower())
                        print str(found_counter) + ' Found Exact Duplicate!'
                    except: 
                        problems.append(directory + str(nzb))
                        error_counter += 1
                        print str(error_counter) + ' Problem Moving ', nzb
                    break
                elif QUALITIES_VALUE[get_episode_quality(nzb)] > QUALITIES_VALUE[get_episode_quality(tv_show_found.file_name)]:
                    try:
                        found_counter += 1
                        win32file.MoveFile(directory + str(nzb), directory+'inferior_quality'+'/'+str(nzb))
                        moved_files.append(nzb.lower())
                        print str(found_counter) + ' Found Partial Duplicate!'
                    except: 
                        problems.append(directory + str(nzb))
                        error_counter += 1
                        print str(error_counter) + ' Problem Moving', nzb
                    break
                else:
                    try:
                        found_counter += 1
                        win32file.MoveFile(directory + str(nzb), directory+'duplicate_2'+'/'+str(nzb))
                        moved_files.append(nzb.lower())
                        print str(found_counter) + ' Found Partial Duplicate!'
                    except: 
                        problems.append(directory + str(nzb))
                        error_counter += 1
                        print str(error_counter) + ' Problem Moving', nzb
                    break


    return moved_files, problems

def is_tv_show(nzb):
    if 'duplicate' in nzb.lower():
        return True
    file_name_parts = nzb.upper().split('.')
    for parts in file_name_parts:
        for season in Seasons:
            if season in parts and season+'E' in parts:
                return True
    
    return False

def choose_better_quality(nzb, all_nzbs):
    
    nzb_file_name_parts = nzb.upper().split('.')
    for nzbs in all_nzbs:
        if nzb.upper() == nzbs.upper():
            pass
        else:
            if nzb.upper().split('.')[0] == nzbs.upper().split('.')[0] and nzb.upper().split('.')[1] == nzbs.upper().split('.')[1]:
                nzbs_file_name_parts = nzbs.upper().split('.')
                
                found = False
                curr_nzb_name = ''
                for parts in nzbs_file_name_parts:
                    for season in Seasons:
                        if season in parts:
                            curr_nzb_name += parts
                            found = True
                            break
                            break
                    if not found:
                        curr_nzb_name += parts + '.'
                
                found = False
                curr_nzbs_name = ''
                for parts in nzb_file_name_parts:
                    for season in Seasons:
                        if season in parts:
                            curr_nzbs_name += parts
                            found = True
                            break
                            break
                    if not found:
                        curr_nzbs_name += parts + '.'
                                    
                if curr_nzb_name == curr_nzbs_name:
                    try:
                        if QUALITIES_VALUE[get_episode_quality(nzbs)] < QUALITIES_VALUE[get_episode_quality(nzb)]:
                            # print str(nzbs)
                            return True
                        elif QUALITIES_VALUE[get_episode_quality(nzbs)] == QUALITIES_VALUE[get_episode_quality(nzb)] and \
                        'REAL' not in nzb.upper() and 'PROPER' not in nzb.upper():
                            if os.path.getsize(nzb) < os.path.getsize(nzbs):
                                # print str(nzbs)
                                return True
                    except:
                        pass
    return False


def is_same_show_season_episode(nzb, episode):
    file_name_parts = nzb.split('.')
    counter = 0
    nzb_name = ''
    found = False
    for parts in file_name_parts:
        for season in Seasons:
            if season in parts:
                nzb_name += parts
                found = True
                break
                break
        if not found:
            nzb_name += parts + '.'
            
    found = False
    file_name_parts = episode.split('.')
    counter = 0
    episode_name = ''
    for parts in file_name_parts:
        for season in Seasons:
            if season in parts:
                episode_name += parts
                found = True
                break
                break
        
        if not found:
            episode_name += parts + '.'
            
    if nzb_name == episode_name:
        try:
            if QUALITIES_VALUE[get_episode_quality(nzb)] >= QUALITIES_VALUE[get_episode_quality(episode)]:
                return True
        except:
            return True
        
    return False

def get_file_names (directory):
    filenames = []
    file_list = []
    for root, dirs, files in os.walk(directory):
        for name in files:
            file_list.append(os.path.join(root, name))
            if name not in filenames and 'RECYCLE' not in str(dir):
                filenames.append(name)   
    return filenames, file_list

def move_files (files, directory):
    moved_file = []
    problems = []
    found_season = False
    counter = 0

    for file in files:
        if os.path.isfile(directory+str(file)) == True :
            found_season = False
            for season in Seasons:
                if season in file and not found_season:
                    found_season = True
                    season_num = season.replace('S', ' ').replace('s', ' ')
                    file_name = str(file).split(season)
                    folder = file_name[0]
                    folder = folder.replace('.', ' ').rstrip()
                    show = directory + folder
                    show_season = show + '/SEASON'+season_num
                    # print show_season, '\n', show
                    try: os.makedirs(show)
                    except: pass
                    try: os.makedirs(show_season)
                    except: pass
                    try:
                        win32file.MoveFile(directory + str(file), show_season+'/'+str(file))
                        moved_file.append(str(file))
                    except win32file.error, e:
                        counter+=1
                        problems.append(str(counter)+'. '+e[2] + ': ' + directory+str(file))
    return moved_file  , problems



def rename_files_simple (directory):
    renamed_files = {}
    counter = 0
    progress_counter = 0
    problems = []
    files = os.listdir(directory)
    print 'Finished Getting files'
    for file in files:
        progress_counter += 1

        if progress_counter % 5000 == 0:
            print 'I am at ', progress_counter
        if os.path.isdir(directory+str(file)):
            continue

        string = str(file)
        string2 = string.lower()
        string2 = string2.replace(' ', '.')
        string2 = string2.replace('-', '.')
        string2 = string2.replace('_', '.')
        string2 = string2.replace('[', '.')
        string2 = string2.replace(']', '.')
        string2 = string2.replace('(', '.')
        string2 = string2.replace(')', '.')
        string2 = string2.replace('.bt.', '.')
        string2 = string2.replace('vtv', '.')
        string2 = string2.replace('..', '.')
        string2 = string2.replace(']', '.')
        string2 = string2.replace('(', '.')
        string2 = string2.replace(')', '.')
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
        string2 = string2.replace('h.264', 'h264')
        string2 = string2.replace('h.s02e64', 'h264')
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
        string2 = string2.replace('.avi.avi', '.avi')
        string2 = string2.replace('.mpg.mpg', '.mpg')
        string2 = string2.replace('.mkv.mkv', '.mkv')
        string2 = string2.replace('.mp4.mp4', '.mp4')
        string2 = string2.replace('}', '.')
        string2 = string2.upper()
        #string2 = string2.replace('I', 'i')
        
        if string != string2 and 'RECYCLE' not in string and 'desktop' not in string:
            counter += 1
            try:
                win32file.MoveFile(directory+string, directory+string2)
                renamed_files[string] = string2
            except:
                if os.path.getsize(directory+string) == os.path.getsize(directory+string2):
                    try:
                        os.remove(directory+string)
                    except:
                        problems.append(str(counter)+' '+directory+str(string2))
                else:
                    problems.append(str(counter)+' '+directory+str(string2))

    return renamed_files, problems
    

def rename_files_complex (directory):
    renamed_files = {}
    problems = []
    counter = 0
    counter_match_three_numbers = 0
    counter_match_three_numbers_x = 0
    match_three_numbers = '\.[0-9][0-9][0-9]\.'
    match_three_numbers_x = '\.[0-9][X][0-9][0-9]\.'
    match_three_numbers_x2 = '\.[0-9][0-9][X][0-9][0-9]\.'
    files = os.listdir(directory)
    for file in files:
        string = str(file)
        match  = re.search(match_three_numbers, string)
        match2 = re.search(match_three_numbers_x, string)
        match3 = re.search(match_three_numbers_x2, string)
        string2 = string
        if match and 'RENO' not in string and '442' not in string and '360' not in string:
            match = match.group()
            string3 = string.split(match)
            money = match[0]+'S0'+match[1]+'E'+match[2]+match[3]+match[4]
            string2 = string3[0] + money + string3[1]
            counter_match_three_numbers += 1
        elif match2:
            match = match2
            match = match.group()
            string3 = string.split(match)
            money = match[0]+'S0'+match[1]+'E'+match[3]+match[4]+match[5]
            string2 = string3[0] + money + string3[1]
            counter_match_three_numbers_x += 1
        elif match3:
            match = match3
            match = match.group()
            string3 = string.split(match)
            money = match[0]+'S'+match[1]+match[2]+'E'+match[4]+match[5]+match[6]
            string2 = string3[0] + money + string3[1]
            counter_match_three_numbers_x += 1
            
        if string != string2 and 'RECYCLE' not in string:
            #check if there is already a season tag on the filename
            has_season = False
            for season in Seasons:
                if season in string:
                    has_season = True
            if not has_season:
                counter += 1
                renamed_files[string] = string2
                try:
                    win32file.MoveFile(directory+string, directory+string2)
                except:
                    problems.append(str(counter)+' '+directory+str(string2))

    problems.append( '\nAll Counter is ' + str(counter))
    problems.append( 'match_three_numbers Counter is ' + str(counter_match_three_numbers))
    problems.append( 'match_three_numbers_x Counter is ' + str(counter_match_three_numbers_x))    
    
    return renamed_files, problems

def catalog_drive (files, drive, directory):
    cataloged = []
    problems = []
    problem_counter = 0
    counter = 0
    
    #Delete all records for this drive
    TV_Shows_Drive.objects.filter(drive=drive).delete()
    
    #Save the drive data
    drive_info = win32file.GetDiskFreeSpaceEx(directory)
    drive = TV_Shows_Drive.objects.create(drive=drive, drive_capacity=int(drive_info[1]) , drive_free_space=int(drive_info[0]))
    
    for file_object in files:
        counter += 1
        try:
            file = str(file_object).rsplit('\\', 1)[1]
        except:
            file = str(file_object)
        if '.NFO' not in file and '.SRT' not in file and '.IDX' not in file and '$' not in file and '.SUB' not in file and 'desktop' not in file:
            file_quality = None
            episode = None
            episode2 = None
            season_object = None
            show_object = None
            found_season = False  
            found_quality = False
            
            for season_nums in Seasons:
                if season_nums in file and not found_season:
                    found_season = True
                    #Save the show data
                    show_name = file.split(season_nums)[0]
                    show_name = show_name.replace('.',' ')
                    show_object = TV_Shows_Name.objects.filter(show=show_name)
                    if not show_object:
                        show_object = TV_Shows_Name.objects.create(drive=drive, show=show_name)
                    else:
                        for shows in show_object:
                            if show_name == shows.show:
                                show_object = shows
                    #if counter == 5:
                        #exit(1)
                    #Save the season and episode data  
                    season = int(season_nums.replace('S', ''))
                    season_object = TV_Shows_Season.objects.filter(drive=drive).filter(show=show_object).filter(season=season)
                    if not season_object: 
                        season_object = TV_Shows_Season.objects.create(drive=drive, show=show_object, season=season)
                    else:
                        for seas in season_object:
                            if season == seas.season:
                                season_object = seas
                    episode_num = file.split(season_nums)[1]
                    episode_num = episode_num.split('.')[0]
                    try:
                        episode=int(episode_num[1]+episode_num[2])
                        try:
                            if episode_num[3] != 'E':
                                episode=int(episode_num[1]+episode_num[2]+episode_num[3])
                        except:
                            pass
                        try:
                            if episode_num[3] == 'E':
                                episode2 = int(episode_num[4]+episode_num[5])
                        except:
                            pass
                    except:
                        episode=None
                    break
                    
            if not found_season:
                show_object=TV_Shows_Name.objects.create(drive=drive, show=file)
                problem_counter += 1
                problems.append(str(problem_counter) + ' ' + file + ' failed to save')  
                    
            file_quality = get_episode_quality(file)
            try:
                episode_filesize = str(os.path.getsize(file_object))
            except:
                episode_filesize = str('0')
            row = TV_Shows.objects.create(drive=drive, 
                                          show=show_object, 
                                          season=season_object,
                                          episode=episode,
                                          quality=file_quality,
                                          file_name=file,
                                          file_size=episode_filesize)

            if episode2:
                row = TV_Shows.objects.create(drive=drive, 
                              show=show_object, 
                              season=season_object,
                              episode=episode2,
                              quality=file_quality,
                              file_name=file,
                              file_size=str(os.path.getsize(file_object)))
                
                                
            cataloged.append(row)
        
    return cataloged, problems

@login_required  
def view_tv_shows(request):
    msg = ''
    duplicate = {}
    duplicates = []
    qduplicate = {}
    qduplicates = []
    all_duplicates = []
    unique = {}
    shows = {}
    drives = {}
    form = {}
    drives = TV_Shows_Drive.objects.all().order_by('drive')
    capacity = 0
    free_space = 0

    for drive in drives:
        capacity += float(drive.drive_capacity)
        free_space += float(drive.drive_free_space)

    if request.method == 'POST':        
        for drive in drives:
            if drive.drive in request.POST:
                values = request.POST.values()
                if "Delete" in values[0]: 
                    print "Deleting " + str(drive.drive)
                    TV_Shows_Drive.objects.filter(drive=drive.drive).delete()
                    drives = TV_Shows_Drive.objects.all().order_by('drive')
                else:
                    shows = TV_Shows_Name.objects.filter(drive=drive).order_by('show')
                    for show in shows:
                        seasons = TV_Shows_Season.objects.filter(show=show).order_by('show')
                        for season in seasons:
                            episodes = TV_Shows.objects.filter(season=season).order_by('episode')
                            unique[str(show.show)+' season '+str(season.season)] = ''
                            for episode in episodes:
                                if str(episode.episode) not in unique[str(show.show)+' season '+str(season.season)]:
                                    unique[str(show.show)+' season '+str(season.season)] = str(episode.episode)
                                elif episode.episode != None:
                                   # duplicate['Show'] = show.show
                                   # duplicate['Season'] = season.season
                                   # duplicate['Episode'] = episode.episode
                                   # duplicate['Path'] = show.show+'/SEASON '+str(season.season).zfill(2)+'/'+episode.file_name
                                   qduplicate = TV_Shows.objects.filter(episode=episode.episode, season__season=season.season, show=show).values('file_name', 'season__season', 'show__show', 'episode', 'id','file_size' )
                                   qduplicates.append(qduplicate)
                                   qduplicate = {}
                                       #duplicates[str(show.show)+' season '+str(season.season)] = str(episode.episode)
                    # if duplicates:
                    #     all_duplicates.append(duplicates)      
    
    return render_to_response('view_tv_shows.html', {   'form'              : form, 
                                                        'drives'            : drives,
                                                        'capacity'          : capacity,
                                                        'free_space'        : free_space,
                                                        'shows'             : shows,
                                                        'msg'               : msg, 
                                                        'qduplicates'    : qduplicates,} )



@login_required  
def delete_episode(request):
    episode_id = request.GET['episode_id']
    drive_letter = request.GET['drive']
    
    try: os.makedirs(drive_letter+':/'+'DuplicateFiles')
    except: pass
    episode = TV_Shows.objects.get(id=episode_id)
    if request.is_ajax():
        mimetype = 'application/javascript'

    path_to_file = drive_letter + ':/' + episode.show.show.rstrip(' ') + '/SEASON ' + str(episode.season.season).zfill(2) + '/' + episode.file_name
    path_to_duplicate = drive_letter + ':/DuplicateFiles/' + episode.file_name
    print path_to_file, path_to_duplicate
    win32file.MoveFile(path_to_file, path_to_duplicate)
    episode.delete()
    return HttpResponse(mimetype)


@login_required
def view_tv_show(request, show_id):
    
    msg = ''
    episodes = {}
    show = TV_Shows_Name.objects.get(id=show_id)
    seasons = TV_Shows_Season.objects.filter(show=show)
    
    for season in seasons:
        episodes[season.season] = TV_Shows.objects.filter(season=season).order_by('episode')
        
    return render_to_response('view_tv_show.html', {'show'      : show,
                                                    'msg'       : msg, 
                                                    'episodes'  : episodes,})

@login_required  
def search_tv_shows(request):
    results = []
    num_of_results = 0
    search = ''
    if request.method == 'POST':
        if request.POST['search']:
            search = request.POST['search'].lower()
            show = TV_Shows_Name.objects.all().order_by('show')
            for episodes in show:
                if search in episodes.show.lower():
                    results.append( episodes )
            num_of_results = results.__len__()
        
    return render_to_response('search_tv_show.html', {'results'         : results,
                                                      'num_of_results'  : num_of_results,
                                                      'search'          : search})

@login_required  
def add_episodes(request, show_id):
    msg = ''
    episodes = {}
    drive = TV_Shows_Drive.objects.get(id=1)
    show = TV_Shows_Name.objects.get(id=show_id)
    seasons = TV_Shows_Season.objects.filter(show=show)
    season = ''
        
    if request.method == 'POST':
        post = dict(request.POST)
        season_post = post['season'][0]
        episode_post = post['episode']
        quality = post['quality']
        file_name = 'WORKING.'+str(show.show.replace(' ', '.'))+'.S0'+str(season_post)+'.E0'
        for avail_seasons in seasons:
            if int(avail_seasons.season) == int(season_post):
                season = avail_seasons
            
        if not season:
            season = TV_Shows_Season.objects.create(drive=drive, show=show, season=season_post)

        for episode in episode_post:
            TV_Shows.objects.create(  drive=drive, 
                                      show=show, 
                                      season=season,
                                      episode=int(episode),
                                      quality=str(quality[0]),
                                      file_name=file_name+str(episode),
                                      file_size=0)
            
    seasons = TV_Shows_Season.objects.filter(show=show)       
    for season_obj in seasons:
        episodes[season_obj.season] = TV_Shows.objects.filter(season=season_obj).order_by('episode')
    
    form = Add_Shows_form()
    return render_to_response('add_episodes.html', {
                                                    'form'      : form,
                                                    'show'      : show,
                                                    'msg'       : msg, 
                                                    'episodes'  : episodes,})
    
def check_existing_files():
    all_files = TV_Shows.objects.all()
    os.chdir('C:/QmA/NZB/TV/ALL_TiLL_JUNE_20_2010/')
    all_nzbs = os.listdir('.')
    tv_show_file_names = []
    nzb_file_names = []
    
    for files in all_files:
        tv_show_file_names.append(files.file_name.rsplit('.', 1)[0])
    print 'got file names\n'
        
    for files in all_nzbs:
        string2 = str(files).rsplit('.', 1)[0]
        string2 = string2.replace(' ', '.')
        string2 = string2.replace('-', '.')
        string2 = string2.replace('_', '.')
        string2 = string2.replace('[', '.')
        string2 = string2.replace(']', '.')
        string2 = string2.replace('(', '.')
        string2 = string2.replace(')', '.')
        string2 = string2.replace('.bt.', '.')
        string2 = string2.replace('.BT.', '.')
        string2 = string2.replace('..', '.')
        string2 = string2.replace('..', '.')
        string2 = string2.replace('\'', '.')
        string2 = string2.replace(',', '.')
        string2 = string2.replace('{', '.')
        string2 = string2.replace('}', '.')
        string2 = string2.upper()
        nzb_file_names.append(string2)
    print 'got nzb file names\n'
                
    counter = 0
    counter2 = 0
    
    for file_name in tv_show_file_names:
        counter2 += 1
        if file_name in nzb_file_names:
            counter += 1
        if counter2 % 1000 == 0:
            print counter2, ' - ', counter
            
    print 'found ', counter, ' nzbs\n'
    
    return

@login_required  
def fix_eps(request):
    msg = ''
    all_missing_shows = []
    missing_shows_counter = 0
    all_missing_qualities = []
    missing_qualities_counter = 0
    better_qualities = []
    better_qualities_counter = 0
    find_quality = ''
    single = []
    missing_show = {}
    shows = []
    seasons = []
    episodes = []
    drives = {}
    form = {}
    drives = TV_Shows_Drive.objects.all().order_by('drive')
    
    if request.method == 'POST': 
        #print request.POST.values()[0]
        if 'Missing Episodes' == request.POST.values()[0]: 
            for drive in drives:
                if drive.drive in request.POST:
                    shows = TV_Shows_Name.objects.filter(drive=drive).order_by('show')
                    for show in shows:
                        seasons = TV_Shows_Season.objects.filter(show=show)
                        for season in seasons:
                            episodes = TV_Shows.objects.filter(season=season).order_by('episode')
                            counter = 1#episodes[0].episode
                            for episode in episodes:
                                if episode.episode:
                                    if counter != episode.episode:
                                        while counter != episode.episode and counter < episode.episode:
                                            missing_show['Show']    = show.show
                                            missing_show['Season']  = season.season
                                            missing_show['Episode'] = counter
                                            season_num = int(season.season)
                                            episode_num = int(counter)
                                            if season_num < 10:
                                                season_num = "0"+str(season_num)
                                            if episode_num < 10:
                                                episode_num = "0"+str(episode_num)
                                            #missing_show['Link']    = "http://binsearch.info/?q="+str(show.show)+"+s"+str(season_num)+"e"+str(episode_num)+"+&max=250&adv_age=&server="
                                            missing_show['Link']    = "http://binsearch.info/?q="+str(show.show)+"+s"+str(season_num)+"e"+str(episode_num)+"+&max=250&adv_age=&server="
                                            single.append(missing_show)
                                            missing_show = {}
                                            counter += 1
                                            missing_shows_counter += 1
                                    counter += 1
                                    
                        if single:
                            all_missing_shows.append(single)
                        single = []
                        
        elif 'Missing Quality' == request.POST.values()[0]: 
            for drive in drives:
                if drive.drive in request.POST:
                    shows = TV_Shows_Name.objects.filter(drive=drive).order_by('show')
                    for show in shows:
                        seasons = TV_Shows_Season.objects.filter(show=show)
                        for season in seasons:
                            episodes = TV_Shows.objects.filter(season=season).order_by('episode')
                            for episode in episodes:
                                if episode.quality == None:
                                    missing_show['Show']    = show.show
                                    missing_show['Season']  = season.season
                                    missing_show['Episode'] = episode.episode
                                    single.append(missing_show)
                                    missing_show = {}
                                    missing_qualities_counter += 1
                                    
                        if single:
                            all_missing_qualities.append(single)
                        single = []
                        
        elif 'Better Quality' == request.POST.values()[0]: 
            for drive in drives:
                if drive.drive in request.POST:
                    shows = TV_Shows_Name.objects.filter(drive=drive).order_by('show')
                    for show in shows:
                        seasons = TV_Shows_Season.objects.filter(show=show)
                        for season in seasons:
                            episodes = TV_Shows.objects.filter(season=season).order_by('episode')
                            best_quality = get_best_quality_episode(episodes)
                            if best_quality:
                                for episode in episodes:
                                    if episode.episode and episode.quality != best_quality:
                                        missing_show['Show']    = show.show
                                        missing_show['Season']  = season.season
                                        missing_show['Episode'] = episode.episode
                                        missing_show['Quality'] = episode.quality
                                        missing_show['Potential'] = best_quality
                                        if best_quality == "HiDEF":
                                            find_quality = "x264"
                                        elif best_quality == "DIGITAL":
                                            find_quality = "dsr"
                                        elif best_quality == "DVD":
                                            find_quality = "dvdrip"
                                        else:
                                            find_quality = best_quality
                                        season_num = int(season.season)
                                        episode_num = int(episode.episode)
                                        if season_num < 10:
                                            season_num = "0"+str(season_num)
                                        if episode_num < 10:
                                            episode_num = "0"+str(episode_num)
                                        missing_show['Link']    = "http://binsearch.info/?q="+str(show.show)+"+s"+str(season_num)+"e"+str(episode_num)+"+&max=250&adv_age=&server="
                                        single.append(missing_show)
                                        missing_show = {}
                                        better_qualities_counter += 1
                                        find_quality = ''
                                    
                        if single:
                            better_qualities.append(single)
                        single = []                        
                    
    return render_to_response('fix_eps.html', { 'form'                      : form, 
                                                'drives'                    : drives,
                                                'shows'                     : shows,
                                                'all_missing_shows'         : all_missing_shows,
                                                'missing_shows_counter'     : missing_shows_counter,
                                                'all_missing_qualities'     : all_missing_qualities,
                                                'missing_qualities_counter' : missing_qualities_counter,
                                                'better_qualities'          : better_qualities,
                                                'better_qualities_counter'  : better_qualities_counter,
                                                'msg'                       : msg, } )    
    

def cleanup_new_files(directory):
    renamed_files = {}
    problems = []
    extension = ''
    counter = 0
    if '0/' not in directory:
        directory = directory + '0/'
        
    files = os.listdir(directory)
    for file in files:
        counter += 1
        # Make sure to ignore system files
        ignore = False 
        string = str(file)
        for item in IGNORE_FILES:
            if item in string.lower():
                ignore = True 
                
        if not ignore:  
            if os.path.isdir(directory+str(file)) == True :
                file_list = []
                file_list = os.listdir(directory+str(file))
                
                if file_list:
                    filetype_counter = 0
                    filetype_file = ''
                    for items in file_list:
                        if os.path.isdir(directory+str(file)+'/'+str(items)) == True:
                            items_files = os.listdir(directory+str(file)+'/'+str(items))
                            for items_file in items_files:
                                try:
                                    win32file.MoveFile(str(directory+str(file)+'/'+str(items)+'/'+str(items_file)), str(directory+str(file)+'/'+str(items_file)))
                                except:
                                    problems.append(str(counter)+' '+items_file)
                        elif items.lower().split('.')[-1] in VALID_FILE_TYPES:
                            if os.path.getsize(str(directory+str(file)+'/'+str(items))) > 40000000:
                                if '.sample.' not in items and '-sample-' not in items and '.sample-' not in items and '-sample.' not in items and 'sample-' not in items:
                                    filetype_counter += 1
                                    filetype_file = items
                                    extension = items.lower().split('.')[-1]
                                else:
                                    win32file.DeleteFile(str(directory+str(file)+'/'+str(items)))
                            else:
                                win32file.DeleteFile(str(directory+str(file)+'/'+str(items)))
                        else:
                            win32file.DeleteFile(str(directory+str(file)+'/'+str(items)))
                    
                    if filetype_counter == 1:
                        if not str(filetype_file) == str(file)+'.'+extension:
                            try:
                                win32file.MoveFile(str(directory+str(file)+'/'+str(filetype_file)), str(directory+str(file)+'/'+str(file)+'.'+extension))
                                renamed_files[str(filetype_file)] = str(file)
                            except:
                                problems.append(str(counter)+' '+file)
                    elif filetype_counter > 1:
                        problems.append(str(counter)+' '+file+ '     -----   FOUND MULTIPLE VIDEO FILES.')
                else:
                    os.rmdir(str(directory+str(file)))

            else: pass
    
    return renamed_files, problems

def move_new_files(directory):
    moved_files = {}
    problems = []
    counter = 0
    main_directory = directory    
    directory = directory + '0/'

    files = os.listdir(directory)
    for file in files:
        counter += 1
        # Make sure to ignore system files
        ignore = False 
        string = str(file)
        for item in IGNORE_FILES:
            if item in string.lower():
                ignore = True 
                
        if not ignore:  
            if os.path.isdir(directory+str(file)) == True :
                file_list = []
                file_list = os.listdir(directory+str(file))
                if file_list:
                    filetype_counter = 0
                    filetype_file = ''
                    for items in file_list:
                        try:
                            win32file.MoveFile(str(directory+str(file)+'/'+str(items)), str(main_directory+'/'+str(items)))
                        except:
                            problems.append(str(counter)+' '+items)
    
    return problems

def get_best_quality_episode(episodes):
    for episode in episodes:
        if episode.quality == 'HiDEF':
            return episode.quality
    for episode in episodes:
        if episode.quality == 'HRHDTV':
            return episode.quality
    for episode in episodes:
        if episode.quality == 'HRPDTV':
            return episode.quality
    for episode in episodes:
        if episode.quality == 'DVD':
            return episode.quality
    for episode in episodes:
        if episode.quality == 'HDTV':
            return episode.quality
    for episode in episodes:
        if episode.quality == 'PDTV':
            return episode.quality
    for episode in episodes:
        if episode.quality == 'DIGITAL':
            return episode.quality
    for episode in episodes:
        if episode.quality == 'TV':
            return episode.quality
    for episode in episodes:
        if episode.quality == 'VCD':
            return episode.quality
        
    return None   
                
def get_episode_quality(file):
    for strings in QUALITIES['HiDEF']:
        if strings in file:
            return 'HiDEF'        
    for strings in QUALITIES['HRHDTV']:
        if strings in file:
            return 'HRHDTV'    
    for strings in QUALITIES['HRPDTV']:
        if strings in file:
            return 'HRPDTV'    
    for strings in QUALITIES['DVD']:
        if strings in file:
            return 'DVD'   
    for strings in QUALITIES['HDTV']:
        if strings in file:
            return 'HDTV'   
    for strings in QUALITIES['PDTV']:
        if strings in file:
            return 'PDTV'     
    for strings in QUALITIES['DIGITAL']:
        if strings in file:
            return 'DIGITAL'    
    for strings in QUALITIES['TV']:
        if strings in file:
            return 'TV'     
    for strings in QUALITIES['VCD']:
        if strings in file:
            return 'VCD'  
        
    return 'UNKNOWN'            