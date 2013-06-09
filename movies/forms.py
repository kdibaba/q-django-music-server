from django import forms
from media.movies.models import *
    
             
class Drive_form(forms.Form):
    ''' Drive Form '''
    drive = forms.CharField ( label = 'Drive', widget=forms.TextInput(attrs={'size':'120'}))
    drive_name = forms.CharField ( label = 'Drive Name', widget=forms.TextInput(attrs={'size':'100'}))
    nzbs = forms.CharField ( label = 'NZB Location', widget=forms.TextInput(attrs={'size':'100'}))