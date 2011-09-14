from django.db import models

# Create your models here.
class Music_Artist(models.Model):
    artist      = models.CharField( max_length = 200 )
    
class Music_Album(models.Model):
    artist      = models.ForeignKey( Music_Artist )
    album       = models.CharField( max_length = 200 ) 
    folder      = models.CharField( max_length = 200 )
    letter      = models.CharField( max_length = 1 )
    year        = models.IntegerField(null=True, blank=True)
    song_count  = models.IntegerField(null=True, blank=True)
    length      = models.CharField( max_length = 50, null=True, blank=True)
    album_art   = models.BooleanField( )    
    
class Music_Song(models.Model):
    album       = models.ForeignKey( Music_Album )
    artist      = models.ForeignKey( Music_Artist )
    filename    = models.CharField( max_length = 200 ) 
    length      = models.CharField( max_length = 50,null=True, blank=True)
    title       = models.CharField( max_length = 400, null=True, blank=True )
    type        = models.CharField( max_length = 200 ) 
    path        = models.CharField( max_length = 400 )
    letter      = models.CharField( max_length = 1 ) 
    rating      = models.IntegerField(null=True, blank=True)