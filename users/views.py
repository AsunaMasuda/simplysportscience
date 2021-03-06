from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login
from django.template.defaultfilters import slugify
from users import forms as user_forms


def register_employer(request):
    '''
    If the form is valid on submition a query is made to check if the email/username
    exists. If it does then a warning message is sent and the form isn't saved.

    The employer registration view takes the forms value of the email field
    and assigns it to the hidden username field.

    After the User is created, a query is made to get the EmployerProfile object
    from the database. Then the information for this model is assigned and saved.

    The new_user is then authenticated and logged in with the form data and
    redirected to a view that routes it to their new profile.

    The registration form is just rendered if the request method is not POST
    '''
    if request.method == "POST":
        form = user_forms.EmployerRegistrationForm(request.POST)
        if form.is_valid():
            if User.objects.filter(username=form.cleaned_data['email']).exists():
                messages.warning(
                    request, "E-mail is already registered!")
            else:
                form_obj = form.save(commit=False)
                form_obj.username = form.cleaned_data.get("email")
                form_obj.save()

                profile = User.objects.filter(
                    username=form_obj.username).first().employerprofile
                profile.is_employer = True
                profile.company_name = form.cleaned_data.get("company_name")
                profile.slug = slugify(form.cleaned_data.get("company_name"))
                profile.save()

                messages.success(
                    request, "Success! Your account has been created.")

                new_user = authenticate(username=form.cleaned_data["email"],
                                        password=form.cleaned_data['password1'],
                                        )
                login(request, new_user)
                return redirect("logged_user_type")
    else:
        form = user_forms.EmployerRegistrationForm()

    context = {
        "form": form,
        "page_title": "For Employers",
    }
    return render(request, "register.html", context)


def register_candidate(request):
    '''
    The candidate registration view is the same as the employer registration view except
    the forms are different and the CandidateProfile fields that are saved are different.
    '''
    if request.method == "POST":
        form = user_forms.CandidateRegistrationForm(request.POST)
        if form.is_valid():
            if User.objects.filter(username=form.cleaned_data['email']).exists():
                messages.warning(
                    request, "E-mail is already registered!")
            else:
                form_obj = form.save(commit=False)
                form_obj.username = form.cleaned_data.get("email")
                form_obj.save()

                profile = User.objects.filter(
                    username=form_obj.username).first().candidateprofile
                profile.is_candidate = True
                profile.first_name = form.cleaned_data.get("first_name")
                profile.last_name = form.cleaned_data.get("last_name")
                profile.save()

                messages.success(
                    request, "Success! Your account has been created.")

                new_user = authenticate(username=form.cleaned_data["email"],
                                        password=form.cleaned_data['password1'],
                                        )
                login(request, new_user)
                return redirect("logged_user_type")
    else:
        form = user_forms.CandidateRegistrationForm()

    context = {
        "form": form,
        "page_title": "For Candidates",
    }
    return render(request, "register.html", context)


def login_view(request):
    '''
    When the LoginForm is submitted and validated the user is authenticated.
    If they are authenticated then they are logged in and redirected to a 
    view that routes them to their specific profile (Employer/Candidate)
    '''
    if request.method == "POST":
        form = user_forms.LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data["email"],
                                password=form.cleaned_data['password'],
                                )
            if user:
                login(request, user)
                messages.success(request, "You have logged in successfully!")
                return redirect("logged_user_type")
            else:
                messages.warning(request, "Your password/email is incorrect")
    else:
        form = user_forms.LoginForm()

    context = {
        "form": form,
        "page_title": "Sign In",
    }
    return render(request, "login.html", context)


@login_required
def logged_user_type(request):
    '''
    This view is used to route the logged in User to their specific profile.
    It trys to access the EmployerProfile of a logged in User. If they dont
    exist then the User is a CandidateProfile and the view name is assigned
    to the user_type. If they exist then the User is an EmployerProfile and
    the view name is assinged to the user_type. Then a redirect is called
    with the user_type.
    '''
    try:
        request.user.employerprofile
    except ObjectDoesNotExist:
        user_type = 'candidate_profile'
    else:
        user_type = 'employer_profile'

    return redirect(user_type)


@login_required
def employer_profile(request):
    '''
    Checks to see if the User is an Employer. If they are not then it
    redirects to the candidate_profile view.

    If they are an employer it renders 2 forms to update the User and
    EmployerProfile objects. The username field is assigned the value
    of the email field automatically.
    '''
    try:
        request.user.employerprofile
    except ObjectDoesNotExist:
        return redirect("candidate_profile")
    else:
        if request.method == "POST":
            update_form = user_forms.EmployerUpdateForm(
                data=request.POST, instance=request.user)
            profile_form = user_forms.EmployerProfileUpdateForm(
                data=request.POST, instance=request.user.employerprofile)
            if update_form.is_valid() and profile_form.is_valid():
                u_form = update_form.save(commit=False)
                u_form.username = update_form.cleaned_data.get("email")
                u_form.save()
                profile_form.save()

                messages.success(
                    request, "Your profile has been updated.")

                context = {
                    "update_form": update_form,
                    "profile_form": profile_form,
                }
                return render(request, "profile.html", context)
        else:
            update_form = user_forms.EmployerUpdateForm(instance=request.user)
            profile_form = user_forms.EmployerProfileUpdateForm(
                instance=request.user.employerprofile)

            context = {
                "update_form": update_form,
                "profile_form": profile_form,
            }

    return render(request, "profile.html", context)


@login_required
def candidate_profile(request):
    '''
    The candidate_profile view is the same as employer_profile view except the
    forms are different. This view only updates the User object because the
    CandidateProfile doesnt have any information that the user should change.
    '''
    try:
        request.user.candidateprofile
    except ObjectDoesNotExist:
        return redirect("employer_profile")
    else:
        if request.method == "POST":
            update_form = user_forms.CandidateUpdateForm(
                data=request.POST, instance=request.user)
            if update_form.is_valid():
                u_form = update_form.save(commit=False)
                u_form.username = update_form.cleaned_data.get("email")
                u_form.save()

                messages.success(
                    request, "Your profile has been updated.")

                context = {
                    "update_form": update_form,
                }
                return render(request, "profile.html", context)
        else:
            update_form = user_forms.CandidateUpdateForm(instance=request.user)
            context = {
                "update_form": update_form,
            }

    return render(request, "profile.html", context)



def employers_page(request):

    context = {
        "page_title": "Employers",
    }
    return render(request, "employers.html", context)


def candidates_page(request):

    context = {
        "page_title": "Candidates",
    }
    return render(request, "candidates.html", context)


def delete_user_view(request):
    '''
    Authenticates the user for confirmation to delete their profile
    '''
    if request.method == "POST":
        form = user_forms.LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data["email"],
                                password=form.cleaned_data['password'],
                                )
            if user:
                request.user.delete()
                messages.success(request, "Your account has been deleted")
                return redirect("jobs")
            else:
                messages.warning(request, "Your password/email is incorrect")
    else:
        form = user_forms.LoginForm()

    context = {
        "form": form,
        "page_title": "Delete Account",
    }
    return render(request, "delete.html", context)
