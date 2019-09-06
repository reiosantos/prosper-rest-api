from django.shortcuts import render


def psp_page_not_found(request, exception):
	return render(request, 'error/404.html', context={'exception': str(exception)}, status=404)


def psp_server_error(request):
	return render(request, 'error/500.html', status=500)


def psp_permission_denied(request, exception):
	return render(request, 'error/403.html', context={'exception': str(exception)}, status=403)


def psp_bad_request(request, exception):
	return render(request, 'error/400.html', context={'exception': str(exception)}, status=400)
