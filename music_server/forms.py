from django import forms


from django.contrib.auth.models import User


class AuthenticationForm(forms.Form):
    ''' Login Form '''
    username = forms.CharField ( label = 'Username')
    password = forms.CharField ( label = 'Password', widget=forms.PasswordInput)
    
    
    
class RegistrationForm(forms.Form):
    ''' Registration Form '''
    first_name      = forms.CharField ( label = 'First Name' )
    last_name       = forms.CharField ( label = 'Last Name' )
    email           = forms.EmailField ( label = 'Email' )
    username        = forms.CharField ( label = 'Username' )
    password        = forms.CharField ( label = 'Password', widget=forms.PasswordInput )  
    retype_password = forms.CharField ( label = 'Retype Password', widget=forms.PasswordInput )    
    
    def clean_username(self):
        if User.objects.filter(username=self.cleaned_data['username']):
            raise forms.ValidationError("That Username is already being used.")