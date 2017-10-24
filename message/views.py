from django.shortcuts import render


def compose(request):
    return render(request, 'base_template.html', {'question': "whu  me"})


def inbox(request):
    return render(request, 'base_template.html', {'question': "whu  me"})


def sent(request):
    return render(request, 'base_template.html', {'question': "whu  me"})
