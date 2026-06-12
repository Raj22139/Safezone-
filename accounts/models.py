from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Extended profile for each registered user."""

    ROLE_CHOICES = [
        ('user',  'Regular User'),
        ('admin', 'Administrator'),
    ]

    user        = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role        = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    phone       = models.CharField(max_length=15, blank=True, null=True)
    city        = models.CharField(max_length=100, blank=True, null=True)
    avatar      = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio         = models.TextField(blank=True, null=True)
    # 2FA Fields
    two_factor_enabled = models.BooleanField(default=False)
    two_factor_secret  = models.CharField(max_length=64, blank=True, null=True)
    backup_codes       = models.TextField(blank=True, null=True)  # JSON stored
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.username} — {self.role}"

    @property
    def full_name(self):
        return self.user.get_full_name() or self.user.username

    @property
    def is_admin(self):
        return self.role == 'admin' or self.user.is_staff


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-create UserProfile whenever a new User is saved."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
