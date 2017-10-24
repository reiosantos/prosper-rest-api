from django.shortcuts import render


def schedule_meeting(request):
    return render(request, 'base_template.html', {'question': "whu  me"})


def all_meetings(request):
    return render(request, 'base_template.html', {'question': "whu  me"})


def new_event(request):
    return render(request, 'base_template.html', {'question': "whu  me"})


def all_events(request):
    return render(request, 'base_template.html', {'question': "whu  me"})
