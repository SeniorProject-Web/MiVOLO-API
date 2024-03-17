from django.db import models

# Create your models here.
class createCustomerServiceModel(models.Model):
    
    ONLY_TOPS = {"dress": "dress",
                "t-shirt": "tShirt",
                "jacket": "jacket",
                "top": "top",
                "long-sleeve": "longSleeve"
                }
    
    ONLY_BOTTOMS = {"short": "short",
                "skirt": "skirt",
                "trouser": "trouser"
                }

    top = models.CharField(max_length=20, choices = ONLY_TOPS)
    pant = models.CharField(max_length=20, choices = ONLY_BOTTOMS)
    time= models.DateField()
    owner = models.EmailField()
    location = models.CharField(max_length=50)
    
    def __str__(self):
        return self.owner
    
    def save(self, *args, **kwargs):
        if self.top == "dress":
            self.pant = "null"
        super(createCustomerServiceModel, self).save(*args, **kwargs)
            
class elementCustomerServiceModel(models.Model):
    ONLY_GENDER = {"Male": "M",
                   "Female": "F",
                   "Unknown": "U"}
    
    ONLY_AGE_GROUP = {
        "15-29": "15-29",
        "30-59": "30-59",
        "60up": "60up",
        "Unknown": "Unknown"
    }
    
    ONLY_TOPS = {"dress": "dress",
                "t-shirt": "tShirt",
                "jacket": "jacket",
                "top": "top",
                "long-sleeve": "longSleeve"
                }
    
    ONLY_BOTTOMS = {"short": "short",
                "skirt": "skirt",
                "trouser": "trouser",
                "None": "None"
                }
    
    image = models.ImageField(upload_to="images/", null=False, blank=True)
    dress = models.IntegerField()
    tShirt = models.IntegerField()
    jacket = models.IntegerField()
    top = models.IntegerField()
    longSleeve = models.IntegerField()
    short = models.IntegerField()
    skirt = models.IntegerField()
    trouser = models.IntegerField()
    finalTop = models.CharField(default = "Unknown", max_length=20, choices = ONLY_TOPS)
    finalBottom = models.CharField(default = "Unknown", max_length=20, choices = ONLY_BOTTOMS)
    gender = models.CharField(default="Unknown", max_length=7, choices = ONLY_GENDER)  
    age = models.CharField(default="Unknown", max_length=7, choices = ONLY_AGE_GROUP)   
    time= models.DateTimeField()
    location = models.CharField(max_length=50)
    
    def __str__(self):
        return f"Customer at {self.location} on {self.time}"
