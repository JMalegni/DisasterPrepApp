from django.shortcuts import render, redirect
from .models import Users

def home(request):
    if request.user.is_authenticated:
        context = { #this is for displaying navbar buttons on homepage
            'authenticated': True,
        }
    else:
        context = {
            'authenticated': False,
        }
    return render(request, 'home.html', context)

def login(request):
    if request.method == 'GET':
        return render(request,'login.html')
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            password = request.POST.get('password')
            #print(email,password)
            user = Users.objects.get(email=email)
            if user.password == password:
                request.session["user_email"] = email
                return redirect('profile')
            else:
                return render(request,'login.html',{'msg':'Enter correct password','tag':'danger'})
        except Users.DoesNotExist:
            return render(request,'login.html',{'msg':'Enter correct email','tag':'danger'})

def signup(request):
    if request.method == 'GET':
        return render(request,'signup.html')

    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            email = request.POST.get('email')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')

            if password != confirm_password:
                return render(request, 'signup.html', {'msg': 'Passwords do not match', 'tag': 'danger'})

            if Users.objects.filter(email = email).exists():
                return render(request, 'signup.html', {'msg': 'Email address is already associated with an account', 'tag': 'danger'})

            request.session['signup_data'] = {
                'name': name,
                'email': email,
                'password': password,
            }

            return redirect('familyinfo')
            #return render(request,'signup.html',{'msg':'Successfully Signup','tag':'success'})

        except Exception:
            return render(request,'signup.html',{'msg':'Error on Signup','tag':'danger'})

def familyinfo(request):
    if request.method == 'GET':
        return render(request, 'familyinfo.html')

    if request.method == 'POST':
        try:
            signup_data = request.session.get('signup_data', {})
            if not signup_data:
                return render(request, 'signup.html', {'msg': 'Please try again'})

            location = request.POST.get('location')
            family_size_str = request.POST.get('family_size')
            family_size = int(family_size_str)

            if family_size < 1 or family_size > 10:
                return render(request, 'familyinfo.html', {'msg': 'Please enter a family size between 1 and 10', 'tag': 'danger'})

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
            return render(request, 'familyinfo.html', {'msg': 'Error on Signup: ' + str(e), 'tag': 'danger'})



def profile(request):
    return render(request,'profile.html')

def allusers (request):
    users_list = Users.objects.all()
    return render(request,'allusers.html',{'list':users_list})

def singleuser(request,id):
    user = Users.objects.get(id=id)
    return render(request,'singleuser.html',{'user':user})

def edituser(request,id):
    if request.method == 'GET':
        user = Users.objects.get(id=id)
        return render(request,'edituser.html',{'user':user})
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = Users.objects.get(id=id)
        user.name = name
        user.password = password
        user.save()
        users_list = Users.objects.all()
        return render(request,'allusers.html',{'list':users_list})

def deleteuser(request,id):
    Users.objects.filter(id=id).delete()
    users_list = Users.objects.all()
    return render(request,'allusers.html',{'list':users_list})

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
            return render(request, 'disasterchecklist.html', {'checklist': checklist})
        except Users.DoesNotExist:
            return redirect('login')

def generate_checklist(user, disaster_type):
    family_size = user.family_size
    checklist = []

    if disaster_type == 'Typhoon':
        checklist = [
            f"{family_size * 3 * 3} Liters of water",
            f"{family_size * 3 * 2000} calories of non-perishable food",
            f"{family_size} sets of clothes (one for each family member)",
            "First aid kit",
            "Important documents (Passport, Will, ID cards)",
            "Cash",
            "Emergency contact list",
            "Radio",
            "Flashlights and batteries",
        ]

        medical_issue = user.medical_issues
        medication_amount = user.medication_amount if user.medication_amount else 0

        if medical_issue and medication_amount == 0:
            checklist.append(f"Medication for {medical_issue} for 3 days")
        elif medical_issue and medication_amount != 0:
            checklist.append(f"Medication for {medical_issue}: {medication_amount * 3} units")

        women = user.women_bool
        baby = user.baby_bool
        child = user.child_bool
        if women:
            checklist.append("Sanitary napkins/tampons")
            checklist.append("Lotion/cleansing sheets")
        if baby:
            checklist.append("Baby formula/food")
            checklist.append("Diapers")
        if child:
            checklist.append("Books/toys")



    elif disaster_type == 'Earthquake':
        checklist = [
            "Secure heavy furniture to walls",
            "Create a family emergency plan",
            "Prepare an emergency bag",
            f"Have enough food and water for {family_size} people for at least 3 days",
            "Keep a whistle to signal for help",
            "Learn basic first aid"
        ]
    elif disaster_type == 'Flood':
        checklist = [
            "Know your evacuation routes",
            "Move valuables to higher ground",
            f"Stock up on {family_size * 3} days of food and water",
            "Prepare an emergency kit with essentials",
            "Ensure you have waterproof bags for important documents",
            "Plan for pets and livestock"
        ]
    else:
        checklist = ["Select a valid disaster type"]

    return checklist

def disasterchecklist(request):
    if request.method == 'GET':
        return render(request, 'disasterchecklist.html')
    if request.method == 'POST':
        return redirect('home')

def logout(request):
    del request.session["user_email"]
    return render(request,'login.html')