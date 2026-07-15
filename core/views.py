import json
import os
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from .models import RSVPSubmission, Person


def index(request):
    photos_dir = os.path.join(settings.BASE_DIR, 'core', 'static', 'core', 'photos', 'o-nas')
    web_exts = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
    o_nas_photos = []
    if os.path.isdir(photos_dir):
        o_nas_photos = sorted([
            f for f in os.listdir(photos_dir)
            if os.path.splitext(f)[1].lower() in web_exts
        ])
    return render(request, 'core/index.html', {'o_nas_photos': o_nas_photos})


def rsvp(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Honeypot — bots fill this in, humans don't see it
            if data.get('hp_name', ''):
                return JsonResponse({'ok': True})
            # Duplicate — same browser session already submitted
            if request.session.get('rsvp_submitted'):
                return JsonResponse({'ok': True})
            submission = RSVPSubmission.objects.create(
                accom_want=data.get('accom_want', ''),
                accom_pref=', '.join(data.get('accom_pref', [])),
                song_request=data.get('song_request', ''),
                message=data.get('message', ''),
            )
            for p in data.get('persons', []):
                Person.objects.create(
                    submission=submission,
                    name=p.get('name', ''),
                    is_child=bool(p.get('is_child', False)),
                    age=p.get('age') or None,
                    diet=', '.join(p.get('diet', [])),
                    other_diet=p.get('other_diet', ''),
                    alcohol=', '.join(p.get('alcohol', [])),
                )
            request.session['rsvp_submitted'] = True
            return JsonResponse({'ok': True})
        except Exception as e:
            return JsonResponse({'ok': False, 'error': str(e)}, status=400)

    already_submitted = request.session.get('rsvp_submitted', False)
    return render(request, 'core/rsvp.html', {'already_submitted': already_submitted})
