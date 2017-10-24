from datetime import datetime, date

from django.contrib.auth.models import Permission
from django.forms.models import BaseModelFormSet


def get_id():
    user_id = date.strftime(datetime.now(), "%y%m%d%H%M")
    return user_id


def get_corrected_permissions(user=None):
    """
    :param user:
    :return:
    """

    perms_to_exclude = ('auth', 'admin', 'contenttypes', 'sessions')
    perms = Permission.objects.all()
    for app_label in perms_to_exclude:
        perms = perms.exclude(content_type__app_label=app_label)

    if user is not None and not user.is_superuser:
        perms = perms.filter(user=user)

    return perms


# This class is used to make empty formset forms required
class RequiredFormset(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super(RequiredFormset, self).__init__(*args, **kwargs)
        for form in self.forms:
            form.empty_permitted = False
