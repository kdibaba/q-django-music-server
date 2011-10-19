from django import forms
from media.music.models import *
    
             
class Drive_form(forms.Form):
    ''' Drive Form '''
    drive = forms.CharField ( label = 'Drive')
    drive_name = forms.CharField ( label = 'Drive Name')
    nzbs = forms.CharField ( label = 'NZB Location')
    directory = forms.CharField ( label = 'Albums Directory')
    
    
        
class UploadFileForm(forms.Form):
    file  = forms.FileField(required=False)    
    file1  = forms.FileField(required=False)    
    file2  = forms.FileField(required=False)    
    file3  = forms.FileField(required=False)    
    file4  = forms.FileField(required=False)    
    file5  = forms.FileField(required=False)    
    file6  = forms.FileField(required=False)   
    file7  = forms.FileField(required=False)    
    file8  = forms.FileField(required=False)    
    file9  = forms.FileField(required=False)    
    file10  = forms.FileField(required=False)     