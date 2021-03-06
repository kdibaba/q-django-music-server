
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from music.views import LETTERS


from media.music.models import *
from media.forms import *
  
def user_login(request):
    theme = 'theme_white'
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(request.POST)
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        user = authenticate(username=username, password=password)
        if user is None:
            message = 'Your username and password didn\'t match. Please try again.'
        else:                
            login(request, user)
            if request.POST.get('home', None):
                return HttpResponseRedirect('/')
            return HttpResponseRedirect( request.META.get('HTTP_REFERER', None) or '/')
    return render_to_response('login.html', locals())

def register_user (request):
    letter_list = LETTERS
    form = RegistrationForm()
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name      = request.POST.get('first_name', None)
            last_name       = request.POST.get('last_name', None)
            email           = request.POST.get('email', None)
            username        = request.POST.get('username', None)
            password        = request.POST.get('password', None)
            retype_password = request.POST.get('retype_password', None)
            
            user = User.objects.create(first_name=first_name , last_name=last_name , email=email , username=username)
            user.set_password(password)
            user.save()
            if user is None:
                message = 'Registration Failed. Please try again.'
            else:
                user_login = authenticate(username=username, password=password)
                login(request, user_login)
                UserProfile.objects.create(user=user, theme='white', song_table_columns=";")
                return HttpResponseRedirect('/') 
    return render_to_response('register.html', locals())

def user_logout(request):
    logout(request)
    return HttpResponseRedirect( request.META.get('HTTP_REFERER', None) or '/')

@login_required
def is_admin(request):
    admin = 0
    if request.user.is_superuser:
        admin = 1
        
    if request.is_ajax():
        mimetype = 'application/javascript'
    return HttpResponse(admin, mimetype)   


def check_session(request):
    status = 0
    if request.user.is_authenticated():
        status = 1
    if request.is_ajax():
        mimetype = 'application/javascript'
    return HttpResponse(status, mimetype) 