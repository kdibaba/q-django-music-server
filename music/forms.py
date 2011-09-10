from django import forms
from media.music.models import *
    
             
class Drive_form(forms.Form):
    ''' Drive Form '''
    drive = forms.CharField ( label = 'Drive')
    drive_name = forms.CharField ( label = 'Drive Name')
    nzbs = forms.CharField ( label = 'NZB Location')
    directory = forms.CharField ( label = 'Albums Directory')