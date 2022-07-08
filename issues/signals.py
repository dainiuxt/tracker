from django.db.models.signals import post_save  # signal
from authuser.models import User                # sender
from django.dispatch import receiver            # receiver (decorator)
from .models import Profile

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs): 
    if created:
        Profile.objects.create(user=instance)
        print('KWARGS: ', kwargs)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()
