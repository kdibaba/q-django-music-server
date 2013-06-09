from django.db import models

# Create your models here.
class TV_Shows_Drive(models.Model):
    """ TV Shows """
    drive               = models.CharField(max_length = 50)
    drive_capacity      = models.CharField(max_length = 200)
    drive_free_space    = models.CharField(max_length = 200)
    drive_date          = models.DateTimeField(auto_now_add=True, null=True, blank=True)

class TV_Shows_Name(models.Model):
    """ TV Shows """
    drive               = models.ForeignKey(TV_Shows_Drive)
    show                = models.CharField(max_length = 200)
    
class TV_Shows_Season(models.Model):
    """ TV Shows """
    drive               = models.ForeignKey(TV_Shows_Drive)
    show                = models.ForeignKey(TV_Shows_Name)
    season              = models.IntegerField(null=True, blank=True ) 
    
class TV_Shows(models.Model):
    """ TV Shows """
    drive               = models.ForeignKey ( TV_Shows_Drive )
    show                = models.ForeignKey ( TV_Shows_Name )
    season              = models.ForeignKey ( TV_Shows_Season, null=True, blank=True ) 
    quality             = models.CharField ( max_length = 200, null=True, blank=True)
    episode             = models.IntegerField ( null=True, blank=True )
    file_name           = models.TextField ()
    file_size           = models.CharField ( max_length = 200 )
    
    def get_file_size (self):
        size = int(self.file_size)/(1024*1024)
        return str(size) + ' MB'