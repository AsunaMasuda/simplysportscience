import json
import stripe
from django.conf import settings
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt


stripe.api_key = settings.STRIPE_SECRET
STRIPE_PUBLISHABLE = settings.STRIPE_PUBLISHABLE
ENDPOINT_SECRET = settings.ENDPOINT_SECRET


@login_required
def checkout_view(request):
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'name': 'Job Post',
            'amount': 10000,
            'currency': 'eur',
            'quantity': 1,
        }],
        success_url='https://simplysportscience.herokuapp.com/checkout/router/',
        cancel_url='https://simplysportscience.herokuapp.com/jobs/search/',
    )
    session_id = session.id

    context = {
        "page_title": "Checkout",
        "STRIPE_PUBLISHABLE": STRIPE_PUBLISHABLE,
        "session_id": session_id,
    }
    return render(request, "checkout.html", context)


@login_required
def credit_view(request):
    profile = request.user.employerprofile
    profile.credits += 1
    profile.save()
    return redirect("new_job")


@csrf_exempt
def webhook_view(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, ENDPOINT_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

    return HttpResponse(status=200)
