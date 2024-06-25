import os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from django.utils.translation import gettext as _
from django.utils.safestring import mark_safe
from .models import Users
import requests
import bleach

ALLOWED_TAGS = ['b', 'i', 'u', 'a', 'ul', 'ol', 'li', 'p', 'br', 'strong', 'em', 'ruby', 'rt']
ALLOWED_ATTRIBUTES = {
    '*': ['class', 'id'],
    'a': ['href', 'title'],
    'ruby': ['lang'],
    'rt': []
}
def sanitize_html(content):
    return bleach.clean(content, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)

APIKey = "5b3ce3597851110001cf6248f1495139fccf4eb9a4494f7bddb5a976"
from .utils import checklist_image

def home(request):
    context = {
        'authenticated': request.user.is_authenticated,
    }
    return render(request, 'home.html', context)

def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            password = request.POST.get('password')
            user = Users.objects.get(email=email)
            if user.password == password:
                request.session["user_email"] = email
                return redirect('profile')
            else:
                return render(request, 'login.html', {'msg': _('Enter correct password'), 'tag': 'danger'})
        except Users.DoesNotExist:
            return render(request, 'login.html', {'msg': _('Enter correct email'), 'tag': 'danger'})

def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html')
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if password != confirm_password:
                return render(request, 'signup.html', {'msg': _('Passwords do not match'), 'tag': 'danger'})

            if Users.objects.filter(email=email).exists():
                return render(request, 'signup.html', {'msg': _('Email address is already associated with an account'), 'tag': 'danger'})

            request.session['signup_data'] = {
                'name': name,
                'email': email,
                'password': password,
            }

            return redirect('familyinfo')

        except Exception:
            return render(request, 'signup.html', {'msg': _('Error on Signup'), 'tag': 'danger'})

def familyinfo(request):
    if request.method == 'GET':
        return render(request, 'familyinfo.html')
    if request.method == 'POST':
        try:
            signup_data = request.session.get('signup_data', {})
            if not signup_data:
                return render(request, 'signup.html', {'msg': _('Please try again'), 'tag': 'danger'})

            location = request.POST.get('location')
            comma_index = location.find(',')
            latitude = location[:comma_index].strip()
            longitude = location[comma_index+1:].strip()
            family_size_str = request.POST.get('family_size')
            family_size = int(family_size_str)

            if family_size < 1 or family_size > 10:
                return render(request, 'familyinfo.html', {'msg': _('Please enter a family size between 1 and 10'), 'tag': 'danger'})

            medical_issues = request.POST.get('medical_issues', '')  # Default to empty string if not provided
            medication_amount_str = request.POST.get('medication_amount', '0')  # Default to '0' if not provided
            medication_amount = int(medication_amount_str) if medication_amount_str else 0  # Ensure it defaults to 0 if empty

            women_bool = request.POST.get('women_bool') == 'on'
            child_bool = request.POST.get('child_bool') == 'on'
            baby_bool = request.POST.get('baby_bool') == 'on'

            user = Users(
                name=signup_data['name'],
                email=signup_data['email'],
                password=signup_data['password'],
                location=location,
                latitude=latitude,
                longitude=longitude,
                family_size=family_size,
                medical_issues=medical_issues,
                medication_amount=medication_amount,
                women_bool=women_bool,
                child_bool=child_bool,
                baby_bool=baby_bool,
            )
            user.save()

            # Automatically log in the user
            request.session['user_email'] = user.email
            del request.session['signup_data']
            return redirect('disasterprep')  # Redirect to disasterprep page

        except Exception as e:
            return render(request, 'familyinfo.html', {'msg': _('Error on Signup: ') + str(e), 'tag': 'danger'})

def profile(request):
    return render(request, 'profile.html')

def deleteuser(request, id):
    Users.objects.filter(id=id).delete()
    return redirect('home')

def disasterprep(request):
    if request.method == 'GET':
        return render(request, 'disasterprep.html')
    if request.method == 'POST':
        disaster_type = request.POST.get('disaster_type')
        email = request.session.get("user_email")
        if not email:
            return redirect('login')

        try:
            user = Users.objects.get(email=email)
            checklist = generate_checklist(user, disaster_type)
            request.session['disaster_type'] = disaster_type
            request.session['checklist'] = checklist
            return render(request, 'disasterchecklist.html', {'checklist': checklist, 'user_id': user.id})
        except Users.DoesNotExist:
            return redirect('login')

def generate_checklist(user, disaster_type):
    family_size = user.family_size
    checklist = []

    if disaster_type == 'Typhoon':
        checklist = [
            f"{family_size * 3 * 3} " + _("Liters of water"),
            f"{family_size * 3 * 2000} " + _("calories of non-perishable food"),
            f"{family_size} " + _("sets of clothes (one for each family member)"),
            _("First aid kit"),
            _("Important documents (Passport, Will, ID cards)"),
            _("Cash"),
            _("Emergency contact list"),
            _("Radio"),
            _("Flashlights and batteries"),
        ]

        medical_issue = user.medical_issues
        sanitized_med = sanitize_html(medical_issue)
        safe_med = mark_safe(sanitized_med)

        medication_amount = user.medication_amount if user.medication_amount else 0

        if medical_issue and medication_amount == 0:
            checklist.append(_("Medication for ") + f"{safe_med} " + _("for 3 days"))
        elif medical_issue and medication_amount != 0:
            checklist.append(_("Medication for ") + f"{safe_med}: {medication_amount * 3} " + _("units"))

        if user.women_bool:
            checklist.append(_("Sanitary napkins/tampons"))
            checklist.append(_("Lotion/cleansing sheets"))
        if user.baby_bool:
            checklist.append(_("Baby formula/food"))
            checklist.append(_("Diapers"))
        if user.child_bool:
            checklist.append(_("Books/toys"))
    elif disaster_type == 'Earthquake':
        checklist = [
            _("Secure heavy furniture to walls"),
            _("Create a family emergency plan"),
            _("Prepare an emergency bag"),
            _("Have enough food and water for ") + f"{family_size} " + _("people for at least 3 days"),
            _("Keep a whistle to signal for help"),
            _("Learn basic first aid")
        ]
    elif disaster_type == 'Flood':
        checklist = [
            _("Know your evacuation routes"),
            _("Move valuables to higher ground"),
            _("Stock up on ") + f"{family_size * 3} " + _("days of food and water"),
            _("Prepare an emergency kit with essentials"),
            _("Ensure you have waterproof bags for important documents"),
            _("Plan for pets and livestock")
        ]
    else:
        checklist = [_("Select a valid disaster type")]

    return checklist

def disasterchecklist(request):
    if request.method == 'GET':
        user_email = request.session.get("user_email")
        if not user_email:
            return redirect('login')

        user = get_object_or_404(Users, email=user_email)
        return render(request, 'disasterchecklist.html', {'user_id': user.id})
    #return redirect('disasterposter', user_id=request.POST.get('user_id'))

def disasterposter(request):
    """response = requests.get(
        f"https://api.openrouteservice.org/v2/directions/driving-car?api_key={APIKey}&start=8.681495,49.41461&end=8.687872,49.420318")
    print(response.status_code)
    print(response.json())"""
    if request.method == 'GET':
        return render(request, 'disasterposter.html')
    
    elif request.method == 'POST':
        #GeoJSON Information
        apiFailed = False
        try:
            response = requests.get(
                f"https://api.openrouteservice.org/v2/directions/driving-car?api_key={APIKey}&start=8.681495,49.41461&end=8.687872,49.420318")
            value = response.json()['features'][0]
            value = str(value).replace("\'", "\"")
        except:
            apiFailed = True

        # Gets disaster type and checklist based on whats saved in the session
        disaster_type = request.session.get('disaster_type')
        checklist = request.session.get('checklist')
        facts = generate_facts(disaster_type)

        if not disaster_type or not checklist:
            return redirect('disasterprep')

        image_name = checklist_image(checklist, disaster_type, facts)
        if image_name and settings.STATIC_URL:
            image_url = f"{settings.STATIC_URL}images/{image_name}"
            if apiFailed:
                context = {'image_url': image_url}
            else:
                context = {'image_url': image_url, 'geoJSON': value}

        else:
            if apiFailed:
                context = {'error_message': 'Error creating checklist'}
            else:
                context = {'error_message': 'Error creating checklist', 'geoJSON': value}

        return render(request, 'disasterposter.html', context)

def generate_facts(disaster_type):
    facts = []

    if (disaster_type == 'Typhoon'):
        facts = [
            _("Typhoon fact 1"),
            _("Typhoon fact 2"),
            _("Typhoon fact 3"),
            _("Typhoon fact 4"),
            _("Typhoon fact 5"),
        ]
    elif (disaster_type == 'Earthquake'):
        facts = [
            _("Earthquake fact 1"),
            _("Earthquake fact 2"),
            _("Earthquake fact 3"),
            _("Earthquake fact 4"),
            _("Earthquake fact 5"),
        ]
    elif (disaster_type == 'Flood'):
        facts = [
            _("Flood fact 1"),
            _("Flood fact 2"),
            _("Flood fact 3"),
            _("Flood fact 4"),
            _("Flood fact 5"),
        ]

    return facts

def download_poster(request):
    image_path = os.path.join(settings.STATIC_ROOT, 'images', 'disaster_poster.png')
    if os.path.exists(image_path):
        with open(image_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='image/png')
            response['Content-Disposition'] = 'attachment; filename="disaster_poster.png"'
            return response
    else:
        return HttpResponse(_("Image not found"), status=404)

def logout(request):
    try:
        del request.session["user_email"]
    except KeyError as err:
        return HttpResponse(_("No user logged in"), status=404)
    return redirect("login")
