from django.contrib import admin
from music.models import *

admin.site.register(Music_Artist)
admin.site.register(Music_Genre)
admin.site.register(Music_Song)
admin.site.register(Music_Playlist)
admin.site.register(UserProfile)
