from django import forms
from media.tv_shows.models import *

QUALITIES = [(u'',u'')]+ [  ('DVD', 'DVD'),
                            ('HiDEF', 'HiDEF'),
                            ('PDTV', 'PDTV'),
                            ('HDTV', 'HDTV'),
                            ('DIGITAL', 'DIGITAL'), ] 

def get_episodes():
    count = 1
    episodes = [('', '')]
    while count != 100:
        episodes += [(count, count)]
        count += 1
    return episodes
    
             
class Drive_form(forms.Form):
    ''' Drive Form '''
    drive_letter = forms.CharField ( label = 'Drive Letter', widget=forms.TextInput(attrs={'size':'10'}))
    drive = forms.CharField ( label = 'Drive Name', widget=forms.TextInput(attrs={'size':'20'}))
    nzbs = forms.CharField ( label = 'NZB Location', widget=forms.TextInput(attrs={'size':'60'}))
    #files = forms.CharField (label = 'files')

class View_Shows_form(forms.Form):
    ''' View Shows Form '''
    drives = forms.CharField ( label = 'Drive Letter')
    shows = forms.CharField ( label = 'Shows')
    seasons = forms.CharField ( label = 'seasons')
    episodes = forms.CharField ( label = 'episodes')    
    
class Add_Shows_form(forms.Form):
    ''' Add Shows Form '''
    season      = forms.CharField ( label = 'Season' ) 
    episode     = forms.MultipleChoiceField ( choices=get_episodes(), widget=forms.SelectMultiple(attrs={'style':'width:50px;', 'size':'10'}) )
    quality     = forms.ChoiceField ( choices=QUALITIES )
