import os
import json
from django.shortcuts import render, get_object_or_404, HttpResponse
from django.db.models import Q
from jobs.models import Job, EmployerProfile

def job_list(request):
    algolia_key = os.environ.get('ALGOLIA_PUBLIC_KEY')
    algolia_app_id = os.environ.get('ALGOLIA_PUBLIC_APP_ID')

    context = {
        "page_title": "Jobs",
        "posts": Job.objects.all(),
        "ALGOLIA_PUBLIC_KEY": algolia_key,
        "ALGOLIA_PUBLIC_APP_ID": algolia_app_id,
    }
    return render(request, "job-list.html", context)

def employer_job_list(request, pk, slug=""):
    employer_object = get_object_or_404(EmployerProfile, pk=pk)

    page_title = employer_object.company_name + " " + "Jobs"
    posts = Job.objects.filter(employer_fk=employer_object)
    algolia_key = os.environ.get('ALGOLIA_PUBLIC_KEY')
    algolia_app_id = os.environ.get('ALGOLIA_PUBLIC_APP_ID')

    context = {
        "page_title": page_title,
        "posts": posts,
        "ALGOLIA_PUBLIC_KEY": algolia_key,
        "ALGOLIA_PUBLIC_APP_ID": algolia_app_id,
    }
    return render(request, "job-list.html", context)

def autocomplete_title_search(request):
    if request.is_ajax():
        job_query = request.GET.get('term', '')
        titles = Job.objects.filter(
            Q(title__istartswith=job_query) | Q(title__icontains=job_query)
        )
        result = []
        for title in titles:
            title_json = title.title
            result.append(title_json)
        data = json.dumps(result)
        mimetype = 'application/json'
    return HttpResponse(data, mimetype)

def search_results(request):
    job_query = request.GET.get('job-title')
    location_query = request.GET.get('location')
    posts = Job.objects.filter(
        title__icontains=job_query, location__icontains=location_query
    )

    if location_query != "":
        page_title = job_query.title() + " Jobs in " + location_query.title()
    else:
        page_title = job_query.title() + " Jobs Everywhere"

    algolia_key = os.environ.get('ALGOLIA_PUBLIC_KEY')
    algolia_app_id = os.environ.get('ALGOLIA_PUBLIC_APP_ID')
    context = {
        "page_title": page_title,
        "posts": posts,
        "ALGOLIA_PUBLIC_KEY": algolia_key,
        "ALGOLIA_PUBLIC_APP_ID": algolia_app_id,
    }
    return render(request, "job-list.html", context)
