from django.db import models

# Create your models here.
class Music_Artist(models.Model):
    artist      = models.CharField( max_length = 200 )
    letter      = models.CharField( max_length = 2 ) 
    

class Music_Genre(models.Model):
    genre      = models.CharField( max_length = 200, unique=True )
        
class Music_Album(models.Model):
    album_artist      = models.ForeignKey( Music_Artist )
    album_genre      = models.ForeignKey( Music_Genre )
    album       = models.CharField( max_length = 200 ) 
    folder      = models.CharField( max_length = 200 )
    album_size  = models.CharField( max_length = 200 )
    letter      = models.CharField( max_length = 2 )
    year        = models.IntegerField(null=True, blank=True)
    song_count  = models.IntegerField(null=True, blank=True)
    length      = models.CharField( max_length = 50, null=True, blank=True)
    album_art   = models.BooleanField( )    
    
    def get_album_size (self):
        if self.album_size:
            size = int(self.album_size)/(1024*1024)
            return str(size) + ' MB'    
    
class Music_Song(models.Model):
    album       = models.ForeignKey( Music_Album )
    song_artist = models.ForeignKey( Music_Artist )
    song_genre = models.ForeignKey( Music_Genre )
    filename    = models.CharField( max_length = 200 )
    file_size   = models.CharField( max_length = 200 ) 
    length      = models.CharField( max_length = 50, null=True, blank=True)
    title       = models.CharField( max_length = 400, null=True, blank=True )
    type        = models.CharField( max_length = 200 ) 
    path        = models.CharField( max_length = 400 )
    letter      = models.CharField( max_length = 2 ) 
    rating      = models.IntegerField(null=True, blank=True)
    
    def get_file_size (self):
        if self.file_size:
            size = int(self.file_size)/(1024*1024)
            return str(size) + ' MB'
    
