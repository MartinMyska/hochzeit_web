import csv
import json
import os
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .models import RSVPSubmission, Person


def index(request):
    web_exts = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

    photos_dir = os.path.join(settings.BASE_DIR, 'core', 'static', 'core', 'photos', 'o-nas')
    o_nas_photos = []
    if os.path.isdir(photos_dir):
        o_nas_photos = sorted([
            f for f in os.listdir(photos_dir)
            if os.path.splitext(f)[1].lower() in web_exts
        ])

    ubyt_photos = []
    for i in range(1, 6):
        folder = os.path.join(settings.BASE_DIR, 'core', 'static', 'core', 'photos', f'ubytovani-{i}')
        photos = []
        if os.path.isdir(folder):
            photos = sorted([
                f for f in os.listdir(folder)
                if os.path.splitext(f)[1].lower() in web_exts
            ])
        ubyt_photos.append(photos)

    return render(request, 'core/index.html', {'o_nas_photos': o_nas_photos, 'ubyt_photos': ubyt_photos})


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


@staff_member_required
def dashboard(request):
    submissions = RSVPSubmission.objects.prefetch_related('persons').order_by('-submitted_at')
    persons = Person.objects.all()

    total_families = submissions.count()
    total_persons = persons.count()
    adults = persons.filter(is_child=False).count()
    children = persons.filter(is_child=True).count()

    want_sleep = Person.objects.filter(submission__accom_want__in=['home', 'sleep']).count()
    want_help = Person.objects.filter(submission__accom_want='help').count()
    want_sleep_fam = submissions.filter(accom_want__in=['home', 'sleep']).count()
    want_help_fam = submissions.filter(accom_want='help').count()
    accom_total = want_sleep + want_help

    accom_counts: dict[str, list] = {}
    for s in submissions:
        person_count = len(s.persons.all())
        for pref in s.accom_pref.split(','):
            pref = pref.strip()
            if pref:
                if pref not in accom_counts:
                    accom_counts[pref] = [0, 0]
                accom_counts[pref][0] += person_count
                accom_counts[pref][1] += 1

    diet_counts: dict[str, int] = {}
    for p in persons:
        for d in p.diet.split(','):
            d = d.strip()
            if d:
                diet_counts[d] = diet_counts.get(d, 0) + 1
        if p.other_diet.strip():
            key = f'Jiné: {p.other_diet.strip()}'
            diet_counts[key] = diet_counts.get(key, 0) + 1

    alcohol_counts: dict[str, int] = {}
    for p in persons:
        for a in p.alcohol.split(','):
            a = a.strip()
            if a:
                alcohol_counts[a] = alcohol_counts.get(a, 0) + 1

    songs = [(s.song_request.strip(), str(s)) for s in submissions if s.song_request.strip()]

    return render(request, 'core/dashboard.html', {
        'total_families': total_families,
        'total_persons': total_persons,
        'adults': adults,
        'children': children,
        'want_sleep': want_sleep,
        'want_help': want_help,
        'want_sleep_fam': want_sleep_fam,
        'want_help_fam': want_help_fam,
        'accom_total': accom_total,
        'accom_counts': sorted((k, v[0], v[1]) for k, v in accom_counts.items()),
        'diet_counts': sorted(diet_counts.items()),
        'alcohol_counts': sorted(alcohol_counts.items()),
        'songs': songs,
        'submissions': submissions,
    })


@staff_member_required
def csv_submissions(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="submissions.csv"'
    w = csv.writer(response)
    w.writerow(['id', 'accom_want', 'accom_pref', 'song_request', 'message', 'submitted_at'])
    for s in RSVPSubmission.objects.order_by('submitted_at'):
        w.writerow([s.pk, s.accom_want, s.accom_pref, s.song_request, s.message, s.submitted_at])
    return response


@staff_member_required
def csv_persons(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="persons.csv"'
    w = csv.writer(response)
    w.writerow(['id', 'submission_id', 'name', 'is_child', 'age', 'diet', 'other_diet', 'alcohol'])
    for p in Person.objects.order_by('submission_id', 'pk'):
        w.writerow([p.pk, p.submission_id, p.name, p.is_child, p.age, p.diet, p.other_diet, p.alcohol])
    return response
