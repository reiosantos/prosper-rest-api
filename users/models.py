
from __future__ import unicode_literals

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _

from config import settings
from home.support.validators import FileValidator, get_id


class User(AbstractUser):
    USER_CHOICES = (
        ('admin', 'Administrator. User will have most of the'
                  ' rites to access this application unless specified otherwise'),
        ('member', 'Other Member. Has only the permissions you assign ')
    )
    USER_STATUS = (
        ('active', 'Active'),
        ('cancelled', 'Cancel Request'),
        ('deleted', 'Exited / delete'),
        ('pending', 'Pending Approval'),
    )
    # these are overriden
    first_name = models.CharField(_('first name'), max_length=30, blank=False)
    last_name = models.CharField(_('last name'), max_length=30, blank=False)
    email = models.EmailField(_('email address'), blank=False)

    contact = models.CharField(max_length=45, blank=False, default=0, help_text='Enter User Phone number')
    account_id = models.CharField(max_length=15, blank=False, unique=True, default=get_id,
                                  help_text='Unique Account Number for user')
    address = models.CharField(max_length=255, blank=False, help_text='Where the user currently lives/stays')
    photo = models.ImageField(db_column='photo',
                              validators=[
                                  FileValidator(
                                      max_size=settings.FILE_UPLOAD_MAX_MEMORY_SIZE,
                                      allowed_extensions=['png', 'jpg', 'jpeg'],
                                      allowed_mimetypes=['image/png', 'image/jpg', 'image/jpeg'], min_size=1)],
                              blank=True, help_text='upload user photo for identity', upload_to='user_photos')
    user_type = models.CharField(blank=False, help_text='Type of user designates if admin or other member',
                                 default='member', max_length=255, choices=USER_CHOICES)
    user_status = models.CharField(max_length=255, help_text='select the current status of the user',
                                   default='pending', choices=USER_STATUS)

    def __unicode__(self):
        return self.first_name + " " + self.last_name

    class Meta(AbstractUser.Meta):
        ordering = ['first_name', 'last_name', 'account_id']
        default_permissions = ('add', 'delete', 'modify', 'view')
        permissions = (
            ('can_not_do_much', 'Just a member'),
        )