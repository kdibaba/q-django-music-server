from django import forms


class AuthenticationForm(forms.Form):
    ''' Login Form '''
    username = forms.CharField ( label = 'Username')
    password = forms.CharField ( label = 'Password', widget=forms.PasswordInput)
    