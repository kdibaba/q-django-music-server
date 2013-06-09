from django.db import models

# Create your models here.
class Movie_Drive(models.Model):
    """ Movie Drive """
    drive               = models.CharField( max_length = 50 )
    drive_capacity      = models.CharField (max_length = 200)
    drive_free_space    = models.CharField (max_length = 200)
    drive_date          = models.DateTimeField(auto_now_add=True, null=True, blank=True)

class Movie_Name(models.Model):
    """ Movie Name """
    drive               = models.ForeignKey( Movie_Drive )
    movie_name          = models.CharField( max_length = 200 )
    file_name           = models.TextField ()
    file_size           = models.CharField ( max_length = 200 )
    
    def get_file_size (self):
        size = int(self.file_size)/(1024*1024)
        return str(size) + ' MB'