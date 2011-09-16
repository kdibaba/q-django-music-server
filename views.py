
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout, login


from media.forms import *
  
def user_login(request):
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
            request.session.set_expiry(9999);
            if request.POST.get('home', None):
                return HttpResponseRedirect('/')
            return HttpResponseRedirect( request.META.get('HTTP_REFERER', None) or '/')
    return render_to_response('login.html', locals())

def user_logout(request):
    logout(request)
    return HttpResponseRedirect( request.META.get('HTTP_REFERER', None) or '/')
