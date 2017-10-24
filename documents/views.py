from django.shortcuts import render


def upload(request):
    return render(request, 'base_template.html', {'question': "whu  me"})


def view_all(request):
    return render(request, 'base_template.html', {'question': "whu  me"})
