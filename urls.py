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
    (r'^add_music/$',                           'media.music.views.handle_music_drive'),
    (r'^artists/$',                             'media.music.views.artists'),
    (r'^albums/$',                              'media.music.views.albums'),
    (r'^album_info/(?P<album_id>\d+)/$',             'media.music.views.album_info'),
    (r'^album/(?P<album_id>\d+)/$',             'media.music.views.album'),
    (r'^albums/(?P<artist_id>\d+)/$',           'media.music.views.albums_by_artist'),
    (r'^search_music/$',                        'media.music.views.search_music'),
#    (r'^play_music/$',                         'Catalog.music.views.play_music'),
#    
#    (r'^handle_movies_drive/$',                 'Catalog.movies.views.handle_movies_drive'),
#    (r'^view_movies/$',                         'Catalog.movies.views.view_movies'),
#    (r'^search_movies/$',                       'Catalog.movies.views.search_movies'),


    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/(.*)', admin.site.root),
)

if settings.DEBUG:
    urlpatterns += patterns( '',
        url( r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT} ),
    )