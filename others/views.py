from django.shortcuts import render


def ideas(request):
    return render(request, 'base_template.html', {'question': "whu  me"})


def market(request):
    return render(request, 'base_template.html', {'question': "whu  me"})
