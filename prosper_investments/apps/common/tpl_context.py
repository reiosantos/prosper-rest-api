from django.conf import settings


def site_vars(request):
	var = {
		'home_page': settings.PSP_DASHBOARD_URL,
		'media_url': settings.MEDIA_URL,
		'title': 'Prosper Investments',
		'company_name': 'Prosper Investments',
	}
	return var
