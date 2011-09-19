from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^Catalog/', include('Catalog.foo.urls')),
    (r'^$',                                     'media.music.views.music'),
    (r'^music/$',                               'media.music.views.music'),
    (r'^login/$',                               'media.views.user_login' ),
    (r'^logout/$',                              'media.views.user_logout' ),
#    
    (r'^add_music/rebuild/$',                   'media.music.views.rebuild_music_db'),
    (r'^add_music/add/$',                       'media.music.views.add_to_music_db'),
      
    (r'^album_info/(?P<album_id>\d+)/$',        'media.music.views.album_info'),
    (r'^album/(?P<album_id>\d+)/$',             'media.music.views.album'),
    (r'^albums/(?P<artist_id>\d+)/$',           'media.music.views.albums_by_artist'),
    (r'^song/(?P<song_id>\d+)/$',               'media.music.views.get_song'),
    
    (r'^rating/(?P<song_id>\d+)/(?P<rating>\d+)/$',           'media.music.views.set_rating'),
    
    (r'^search_music/$',                        'media.music.views.search_music'),
    (r'^artists/A/$',                           'media.music.views.artists', {'letter': 'A'}),
    (r'^artists/B/$',                           'media.music.views.artists', {'letter': 'B'}),
    (r'^artists/C/$',                           'media.music.views.artists', {'letter': 'C'}),
    (r'^artists/D/$',                           'media.music.views.artists', {'letter': 'D'}),
    (r'^artists/E/$',                           'media.music.views.artists', {'letter': 'E'}),
    (r'^artists/F/$',                           'media.music.views.artists', {'letter': 'F'}),
    (r'^artists/G/$',                           'media.music.views.artists', {'letter': 'G'}),
    (r'^artists/H/$',                           'media.music.views.artists', {'letter': 'H'}),
    (r'^artists/I/$',                           'media.music.views.artists', {'letter': 'I'}),
    (r'^artists/J/$',                           'media.music.views.artists', {'letter': 'J'}),
    (r'^artists/K/$',                           'media.music.views.artists', {'letter': 'K'}),
    (r'^artists/L/$',                           'media.music.views.artists', {'letter': 'L'}),
    (r'^artists/M/$',                           'media.music.views.artists', {'letter': 'M'}),
    (r'^artists/N/$',                           'media.music.views.artists', {'letter': 'N'}),
    (r'^artists/O/$',                           'media.music.views.artists', {'letter': 'O'}),
    (r'^artists/P/$',                           'media.music.views.artists', {'letter': 'P'}),
    (r'^artists/Q/$',                           'media.music.views.artists', {'letter': 'Q'}),
    (r'^artists/R/$',                           'media.music.views.artists', {'letter': 'R'}),
    (r'^artists/S/$',                           'media.music.views.artists', {'letter': 'S'}),
    (r'^artists/T/$',                           'media.music.views.artists', {'letter': 'T'}),
    (r'^artists/U/$',                           'media.music.views.artists', {'letter': 'U'}),
    (r'^artists/V/$',                           'media.music.views.artists', {'letter': 'V'}),
    (r'^artists/W/$',                           'media.music.views.artists', {'letter': 'W'}),
    (r'^artists/X/$',                           'media.music.views.artists', {'letter': 'X'}),
    (r'^artists/Y/$',                           'media.music.views.artists', {'letter': 'Y'}),
    (r'^artists/Z/$',                           'media.music.views.artists', {'letter': 'Z'}),
    (r'^artists/all/$',                           'media.music.views.artists', {'letter': 'all'}),
    
    (r'^albums/A/$',                           'media.music.views.albums', {'letter': 'A'}),
    (r'^albums/B/$',                           'media.music.views.albums', {'letter': 'B'}),
    (r'^albums/C/$',                           'media.music.views.albums', {'letter': 'C'}),
    (r'^albums/D/$',                           'media.music.views.albums', {'letter': 'D'}),
    (r'^albums/E/$',                           'media.music.views.albums', {'letter': 'E'}),
    (r'^albums/F/$',                           'media.music.views.albums', {'letter': 'F'}),
    (r'^albums/G/$',                           'media.music.views.albums', {'letter': 'G'}),
    (r'^albums/H/$',                           'media.music.views.albums', {'letter': 'H'}),
    (r'^albums/I/$',                           'media.music.views.albums', {'letter': 'I'}),
    (r'^albums/J/$',                           'media.music.views.albums', {'letter': 'J'}),
    (r'^albums/K/$',                           'media.music.views.albums', {'letter': 'K'}),
    (r'^albums/L/$',                           'media.music.views.albums', {'letter': 'L'}),
    (r'^albums/M/$',                           'media.music.views.albums', {'letter': 'M'}),
    (r'^albums/N/$',                           'media.music.views.albums', {'letter': 'N'}),
    (r'^albums/O/$',                           'media.music.views.albums', {'letter': 'O'}),
    (r'^albums/P/$',                           'media.music.views.albums', {'letter': 'P'}),
    (r'^albums/Q/$',                           'media.music.views.albums', {'letter': 'Q'}),
    (r'^albums/R/$',                           'media.music.views.albums', {'letter': 'R'}),
    (r'^albums/S/$',                           'media.music.views.albums', {'letter': 'S'}),
    (r'^albums/T/$',                           'media.music.views.albums', {'letter': 'T'}),
    (r'^albums/U/$',                           'media.music.views.albums', {'letter': 'U'}),
    (r'^albums/V/$',                           'media.music.views.albums', {'letter': 'V'}),
    (r'^albums/W/$',                           'media.music.views.albums', {'letter': 'W'}),
    (r'^albums/X/$',                           'media.music.views.albums', {'letter': 'X'}),
    (r'^albums/Y/$',                           'media.music.views.albums', {'letter': 'Y'}),
    (r'^albums/Z/$',                           'media.music.views.albums', {'letter': 'Z'}),
    (r'^albums/all/$',                           'media.music.views.albums', {'letter': 'all'}),
)

if settings.DEBUG:
    urlpatterns += patterns( '',
        url( r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT} ),
    )