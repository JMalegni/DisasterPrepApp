import os
import time
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.conf import settings
from django.utils.translation import gettext as _
from django.utils.safestring import mark_safe
from .models import Users
import requests
import bleach
import math
from threading import Thread

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
            pet_bool = request.POST.get('pet_bool') == 'on'

            blind_bool = request.POST.get('blind_bool') == 'on'
            deaf_bool = request.POST.get('deaf_bool') == 'on'
            wheelchair_bool = request.POST.get('wheelchair_bool') == 'on'

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
                pet_bool=pet_bool,
                blind_bool=blind_bool,
                deaf_bool=deaf_bool,
                wheelchair_bool=wheelchair_bool,
            )
            user.save()

            # Automatically log in the user
            request.session['user_email'] = user.email
            del request.session['signup_data']
            return redirect('disasterprep')  # Redirect to disasterprep page

        except Exception as e:
            return render(request, 'familyinfo.html', {'msg': _('Error on Signup: ') + str(e), 'tag': 'danger'})

def profile(request):
    if request.method == 'GET':
        email = request.session.get("user_email")
        user = Users.objects.get(email=email)
        context = {'email': user.email,
                   'name': user.name,
                   'password': user.password,
                   'longitude': user.longitude,
                   'latitude': user.latitude,
                   'size': user.family_size,
        }
        if user.medical_issues != "":
            context.update({'medical_issue': user.medical_issues, 'amount': user.medication_amount})
        if user.women_bool:
            context.update({'women': True})
        if user.child_bool:
            context.update({'child': True})
        if user.baby_bool:
            context.update({'baby': True})
        return render(request, 'profile.html', context)
    if request.method == 'POST':
        email = request.session.get("user_email")
        user = Users.objects.get(email=email)

        name = request.POST.get('name')
        new_email = request.POST.get('email')
        password = request.POST.get('password')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        family_size = request.POST.get('size')
        dose = request.POST.get('dose')
        medicine = request.POST.get('medicine')
        women = request.POST.get('women')
        child = request.POST.get('child')
        baby = request.POST.get('baby')
        Users.objects.filter(email=email).update(name=name, email=new_email, password=password, latitude=latitude, longitude=longitude, family_size=family_size)
        request.session["user_email"] = new_email
        if medicine != "no medicine" and int(dose) != 0:
            Users.objects.filter(email=email).update(medication_amount=int(dose), medical_issues=medicine)

        if women != None:
            Users.objects.filter(email=email).update(women_bool=True)
        else:
            Users.objects.filter(email=email).update(women_bool=False)

        if child != None:
            Users.objects.filter(email=email).update(child_bool=True)
        else:
            Users.objects.filter(email=email).update(child_bool=False)

        if baby != None:
            Users.objects.filter(email=email).update(baby_bool=True)
        else:
            Users.objects.filter(email=email).update(baby_bool=False)

        # Build Context
        context = {'email': new_email,
                   'name': name,
                   'password': password,
                   'longitude': longitude,
                   'latitude': latitude,
                   'size': family_size,
                   }
        if medicine != "no medicine":
            context.update({'medical_issue': medicine, 'amount': dose})
        if women != None:
            context.update({'women': True})
        if child != None:
            context.update({'child': True})
        if baby != None:
            context.update({'baby': True})

        return render(request, 'profile.html', context)

def delete_medical(request):
    if request.method == 'POST':
        email = request.session.get("user_email")
        user = Users.objects.get(email=email)
        Users.objects.filter(email=email).update(medication_amount=int(0), medical_issues="")

        # Build Context
        context = {'email': user.email,
                   'name': user.name,
                   'password': user.password,
                   'longitude': user.longitude,
                   'latitude': user.latitude,
                   'size': user.family_size,
                   }
        if user.women_bool:
            context.update({'women': True})
        if user.child_bool:
            context.update({'child': True})
        if user.baby_bool:
            context.update({'baby': True})

        return render(request, 'profile.html', context)

def delete_account(request):
    if request.method == 'POST':
        email = request.session.get("user_email")
        Users.objects.filter(email=email).delete()
        del request.session["user_email"]
        return redirect("home")

def deleteuser(request, id):
    Users.objects.filter(id=id).delete()
    return redirect('home')

def disasterprep(request):
    if request.method == 'GET':
        return render(request, 'disasterprep.html')
    if request.method == 'POST':
        disaster_type = request.POST.get('disaster_type')
        prepare_type = request.POST.get('prepare_type')
        email = request.session.get("user_email")
        if not email:
            return redirect('login')

        try:
            user = Users.objects.get(email=email)
            categories = generate_checklist(user, disaster_type, prepare_type)
            request.session['disaster_type'] = disaster_type
            request.session['checklist'] = categories
            request.session['prepare_type'] = prepare_type

            return render(request, 'disasterchecklist.html', {'categories': categories, 'user_id': user.id})
        except Users.DoesNotExist:
            return redirect('login')

def split_checklist(checklist):
    # Function to split the checklist into three approximately equal parts
    length = len(checklist)
    col1 = checklist[:length//3]
    col2 = checklist[length//3:2*length//3]
    col3 = checklist[2*length//3:]
    return col1, col2, col3

def generate_checklist(user, disaster_type, prepare_type):
     family_size = user.family_size

     if disaster_type == 'Typhoon':
         categories = {
             "Water and Food": [],
             "Clothing and Essentials": [],
             "Medical and Hygiene": [],
         }

         if prepare_type == 'Evacuation Shelter':
             categories["Go Bag"] = []
             categories["Go Bag"].extend([
                 _("Medium-sized backpack/sturdy tote"),
                 _("Two 1-liter bottles"),
                 _("High-calorie bars"),
                 _("Small first aid kit, masks, hand sanitizer"),
                 _("Rain poncho and towel"),
                 _("Small flashlight + multi-tool + whistle"),
             ])
         elif prepare_type == 'Hotel':
             categories["Go Bag"] = []
             categories["Go Bag"].extend([
                 _("Medium-sized backpack/sturdy tote"),
                 _("Two 1-liter bottles"),
                 _("High-calorie bars"),
                 _("Small first aid kit, a few masks, and a small hand sanitizer"),
                 _("Rain poncho and towel"),
                 _("Small flashlight + multi-tool + whistle"),
             ])
         categories["Water and Food"].extend([
             f"{family_size * 3 * 3} " + _("Liters of water"),
             f"{family_size * 3 * 2000} " + _("calories of non-perishable food"),
         ])
         categories["Clothing and Essentials"].extend([
             f"{family_size} " + _("sets of clothes (one for each family member)"),
             _("Important documents (Passport, Will, ID cards)"),
             _("Cash"),
             _("Emergency contact list"),
             _("Radio"),
             _("Flashlights and batteries"),
         ])
         categories["Medical and Hygiene"].append(_("First aid kit"))

         medical_issue = user.medical_issues
         sanitized_med = sanitize_html(medical_issue)
         safe_med = mark_safe(sanitized_med)
         medication_amount = user.medication_amount if user.medication_amount else 0

         if medical_issue and medication_amount == 0:
             categories["Medical and Hygiene"].append(_("Medication for ") + f"{safe_med} " + _("for 3 days"))
         elif medical_issue and medication_amount != 0:
             categories["Medical and Hygiene"].append(_("Medication for ") + f"{safe_med}: {medication_amount * 3} " + _("units"))

         if user.women_bool:
             categories["Medical and Hygiene"].extend([
                 _("Sanitary napkins/tampons"),
                 _("Lotion/cleansing sheets"),
             ])
         if user.baby_bool:
             categories["Medical and Hygiene"].extend([
                 _("Baby formula/food"),
                 _("Diapers"),
             ])
         if user.child_bool:
             categories["Clothing and Essentials"].append(_("Books/toys"))

         if user.pet_bool:
             categories["Pet"] = []
             categories["Pet"].extend([
                 _("Pet food for 3 days"),
                 _("Leash"),
                 _("Pet Sheets"),
                 _("Poop bags"),
             ])
         if user.blind_bool:
            if "Disability" in categories:
               categories["Disability"].extend([
                    _("Mark emergency supplies with Braille labels or large print"),
                    _("Extra eyeglasses or contacts"),
               ])

            else:
                categories["Disability"] = []
                categories["Disability"].extend([
                    _("Mark emergency supplies with Braille labels or large print"),
                    _("Extra eyeglasses or contacts"),

                ])

         if user.deaf_bool:
            if "Disability" in categories:
               categories["Disability"].extend([
                    _("Weather radio with text display and a flashing alert"),
                    _("Extra hearing-aid batteries"),
                    _("Pen and paper for communication"),
                    _("Battery operated lantern to enable communication by sign language"),
               ])

            else:
                categories["Disability"] = []
                categories["Disability"].extend([
                    _("Weather radio with text display and a flashing alert"),
                    _("Extra hearing-aid batteries"),
                    _("Pen and paper for communication"),
                    _("Battery operated lantern to enable communication by sign language"),
                ])

         if user.wheelchair_bool:
            if "Disability" in categories:
               categories["Disability"].extend([
                   _("Weather radio with text display and a flashing alert"),
                   _("Extra hearing-aid batteries"),
                   _("Pen and paper for communication"),
                   _("Battery operated lantern to enable communication by sign language"),
               ])

            else:
                categories["Disability"] = []
                categories["Disability"].extend([
                    _("Backup lightweight manual wheelchair"),
                    _("patch kit or can of sealant for flat tires"),
                    _("Cane or walker"),
                ])




     elif disaster_type == 'Earthquake':
         categories = {
             "Go Bag": [],
             "Water and Food": [],
             "Clothing and Essentials": [],
             "Medical and Hygiene": [],
             "Pet": [],
             "Other": [],
         }

         categories["Other"].extend([
             _("Secure heavy furniture to walls"),
             _("Create a family emergency plan"),
             _("Prepare an emergency bag"),
             _("Have enough food and water for ") + f"{family_size} " + _("people for at least 3 days"),
             _("Keep a whistle to signal for help"),
             _("Learn basic first aid")
         ])

     elif disaster_type == 'Flood':
         categories = {
             "Go Bag": [],
             "Water and Food": [],
             "Clothing and Essentials": [],
             "Medical and Hygiene": [],
             "Pet": [],
             "Other": [],
         }
         categories["Other"].extend([
             _("Know your evacuation routes"),
             _("Move valuables to higher ground"),
             _("Stock up on ") + f"{family_size * 3} " + _("days of food and water"),
             _("Prepare an emergency kit with essentials"),
             _("Ensure you have waterproof bags for important documents"),
             _("Plan for pets and livestock")
         ])

     else:
         categories = {
             "Other": [_("Select a valid disaster type")]
         }

     return categories

def disasterchecklist(request):
    if request.method == 'GET':
        user_email = request.session.get("user_email")
        if not user_email:
            return redirect('login')

        user = get_object_or_404(Users, email=user_email)
        return render(request, 'disasterchecklist.html', {'user_id': user.id})
    #return redirect('disasterposter', user_id=request.POST.get('user_id'))

def api_request(user_location, shelter_coord, result):
    #  First result is if the API failed, second is the value if it succeeded
    response_code = -1
    try:
        response = ""
        while response_code != 200:
            response = requests.get(
                f"https://api.openrouteservice.org/v2/directions/driving-car?api_key={APIKey}&start={user_location[1]},{user_location[0]}&end={shelter_coord[1]},{shelter_coord[0]}")
            response_code = int(response.status_code)
            #  To not overload the system
            if response_code != 200:
                time.sleep(10)
        value = response.json()['features'][0]
        value = str(value).replace("\'", "\"")
        result.append(False)
        result.append(value)
    except:
        result.append(True)

def disasterposter(request):
    """response = requests.get(
        f"https://api.openrouteservice.org/v2/directions/driving-car?api_key={APIKey}&start=8.681495,49.41461&end=8.687872,49.420318")
    print(response.status_code)
    print(response.json())"""
    if request.method == 'GET':
        return render(request, 'disasterposter.html')

    elif request.method == 'POST':
        #Find the closest shelter first
        email = request.session.get("user_email")
        user = Users.objects.get(email=email)
        user_location = [user.latitude, user.longitude]
        shelter_coord = closest_shelter(user_location)
        middle_coord = [(user_location[0] + shelter_coord[0]) / 2.0, (user_location[1] + shelter_coord[1]) / 2.0]

        #GeoJSON Information
        result = []
        api_thread = Thread(target=api_request, args=(user_location, shelter_coord, result))
        api_thread.start()

        # Gets disaster type and checklist based on whats saved in the session
        disaster_type = request.session.get('disaster_type')
        checklist = request.session.get('checklist')
        facts = generate_facts(disaster_type)

        if not disaster_type or not checklist:
            return redirect('disasterprep')

        image_name = checklist_image(checklist, disaster_type, facts)
        if image_name and settings.STATIC_URL:
            image_url = f"{settings.STATIC_URL}images/{image_name}"
            api_thread.join()
            apiFailed = result[0]
            if apiFailed:
                context = {'image_url': image_url}
            else:
                value = result[1]
                context = {'image_url': image_url,
                           'geoJSON': value,
                           'center_lat': middle_coord[0],
                           'center_log': middle_coord[1],
                           'user_lat': user_location[0],
                           'user_log': user_location[1],
                           'shelter_lat': shelter_coord[0],
                           'shelter_log': shelter_coord[1]
                           }

        else:
            api_thread.join()
            apiFailed = result[0]
            if apiFailed:
                context = {'error_message': 'Error creating checklist'}
            else:
                value = result[1]
                context = {'error_message': 'Error creating checklist',
                           'geoJSON': value,
                           'center_lat': middle_coord[0],
                           'center_log': middle_coord[1],
                           'user_lat': user_location[0],
                           'user_log': user_location[1],
                           'shelter_lat': shelter_coord[0],
                           'shelter_log': shelter_coord[1]
                           }

        return render(request, 'disasterposter.html', context)

def thread_closest(user_cord, shelter_cords, result):
    closest = [-1, -1]
    closest_dist = float('inf')
    for cord in shelter_cords:
        curr_dist = math.dist(cord, user_cord)
        if curr_dist < closest_dist:
            closest_dist = curr_dist
            closest = cord
    result.append(closest)

def closest_shelter(user_cord):
    n = 5  # Number of threads to create
    with open("Coordinates.txt", encoding="utf-8") as file:
        addrs = file.readlines()

        # Get the coordinates and split them into n equal lists
        cords = []
        for addr in addrs:
            temp = addr.split()
            temp[0] = float(temp[0])
            temp[1] = float(temp[1])
            cords.append(temp)
        thread_list_length = math.ceil(float(len(cords))/float(n))
        thread_cords = []
        for i in range(n):
            thread_cords.append(cords[thread_list_length * i:thread_list_length * (i + 1)])

        # Threading is magic
        results = []
        threads = []
        for i in range(n):
            threads.append(Thread(target=thread_closest, args=(user_cord,thread_cords[i],results)))
            threads[-1].start()

        # Wait
        [thread.join() for thread in threads]

        #Find the closest of the threads
        closest = [-1, -1]
        closest_dist = float('inf')
        for cord in results:
            curr_dist = math.dist(cord, user_cord)
            if curr_dist < closest_dist:
                closest_dist = curr_dist
                closest = cord

        return closest

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
