
from config import prosper


def site_vars(request):
    var = {
        'TITLE': prosper.COMPANY_TITLE,
        'COMPANY_NAME': prosper.COMPANY_NAME,
        'COMPANY_EMAIL': prosper.COMPANY_EMAIL,
        'COMPANY_CONTACT': prosper.COMPANY_CONTACT,
    }
    return var
