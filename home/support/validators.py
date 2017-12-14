import random

import magic
import mimetypes
from os.path import splitext

from datetime import datetime, date

from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.forms.models import BaseModelFormSet
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import filesizeformat


@deconstructible
class FileValidator(object):
    """
    Validator for files, checking the size, extension and mimetype.
    Initialization parameters:
        allowed_extensions: iterable with allowed file extensions ie. ('txt', 'doc')
        allowd_mimetypes: iterable with allowed mimetypes ie. ('image/png', )
        min_size: minimum number of bytes allowed ie. 100
        max_size: maximum number of bytes allowed ie. 24*1024*1024 for 24 MB

    Usage example::
        MyModel(p_models.Model):
            myfile = FileField(validators=FileValidator(max_size=24*1024*1024), ...)
    """

    extension_message = _("Extension '%(extension)s' not allowed. Allowed extensions are: '%(allowed_extensions)s.'")
    mime_message = _("MIME type '%(mimetype)s' is not valid. Allowed types are: %(allowed_mimetypes)s.")
    min_size_message = _('The current file %(size)s, is too small. The minumum file size is %(allowed_size)s.')
    max_size_message = _('The current file %(size)s, is too large. The maximum file size is %(allowed_size)s.')

    def __init__(self, *args, **kwargs):
        self.allowed_extensions = kwargs.pop('allowed_extensions', None)
        self.allowed_mimetypes = kwargs.pop('allowed_mimetypes', None)
        self.min_size = kwargs.pop('min_size', 0)
        self.max_size = kwargs.pop('max_size', None)

    def __call__(self, value):
        # Check the extension
        ext = splitext(value.name)[1][1:].lower()
        if self.allowed_extensions and ext not in self.allowed_extensions:
            message = self.extension_message % {
                'extension': ext,
                'allowed_extensions': ', '.join(self.allowed_extensions)
            }
            raise ValidationError(message)

        # Check the content type using built in python method
        mimetype = mimetypes.guess_type(value.name)[0]
        if self.allowed_mimetypes and mimetype not in self.allowed_mimetypes:
            message = self.mime_message % {
                'mimetype': mimetype,
                'allowed_mimetypes': ', '.join(self.allowed_mimetypes)
            }
            raise ValidationError(message)

        # Check the content type using magic
        if self.allowed_mimetypes:
            mimetype = magic.from_buffer(value.read(), mime=True)
            if mimetype not in self.allowed_mimetypes:
                message = self.mime_message % {
                    'mimetype': mimetype,
                    'allowed_mimetypes': ', '.join(self.allowed_mimetypes)
                }
                raise ValidationError(message)

        # Check the file size
        filesize = len(value)
        if self.max_size and filesize > self.max_size:
            message = self.max_size_message % {
                'size': filesizeformat(filesize),
                'allowed_size': filesizeformat(self.max_size)
            }
            raise ValidationError(message)

        elif filesize < self.min_size:
            message = self.min_size_message % {
                'size': filesizeformat(filesize),
                'allowed_size': filesizeformat(self.min_size)
            }
            raise ValidationError(message)


def get_id():
    user_id = date.strftime(datetime.now(), "%y%m%d%H%M")
    return user_id


def generate_report_filename():
    return 'report_' + get_id() + '_' + str(random.randint(1, 61)) + str(random.randint(62, 100))


def get_corrected_permissions(user=None):
    """
    :param user:
    :return:
    """
    fill = (
            ~Q(content_type__app_label='admin') &
            ~Q(content_type__app_label='auth') &
            ~Q(content_type__app_label='contenttypes') &
            ~Q(content_type__app_label='sessions'))

    perms = Permission.objects.filter(fill)
    if user is not None and not user.is_superuser:
        perms = perms.filter(user=user)
    return perms


def get_corrected_permissions_tuples(user=None):
    permissions = get_corrected_permissions(user)
    data = {}
    for perm in permissions:
        if perm.content_type.model not in data.keys():
            data[perm.content_type.model] = []
        data[perm.content_type.model].append((perm.id, perm.name))
    return data


# This class is used to make empty formset forms required
class RequiredFormset(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super(RequiredFormset, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False
