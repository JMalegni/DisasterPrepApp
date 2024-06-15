from django.shortcuts import render
from .models import Users

# Create your views here.

def home(request):
    return render(request,'home.html')

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
                return render(request,'profile.html')
            else:
                return render(request,'login.html',{'msg':'Enter correct password','tag':'danger'})
        except Exception:
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

            return render(request, 'familyinfo.html')
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

            user = Users()
            user.name = signup_data['name']
            user.email = signup_data['email']
            user.password = signup_data['password']
            user.location = location
            user.family_size = family_size
            user.save()

            del request.session['signup_data']
            return render(request, 'profile.html')

        except Exception:
            return render(request,'familysize.html',{'msg':'Error on Signup','tag':'danger'})

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
    # Example checklist generation logic
    checklist = []
    if disaster_type == 'Disaster 1':
        checklist = [
            "Stock up on non-perishable food items",
            "Prepare a first aid kit",
            "Secure important documents",
            f"Ensure there is enough water for {user.family_size} people",
            "Create an emergency contact list"
        ]
    elif disaster_type == 'Disaster 2':
        checklist = [
            "Evacuate the area",
            "Prepare an emergency bag",
            "Check local emergency alerts",
            "Plan for pets and livestock",
            "Backup computer data"
        ]
    elif disaster_type == 'Disaster 3':
        checklist = [
            "Reinforce your home",
            "Stay informed about weather updates",
            "Prepare for power outages",
            "Ensure medical supplies are on hand",
            f"Create a communication plan for {user.family_size} people"
        ]
    else:
        checklist = ["Select a valid disaster type"]

    return checklist

def disasterchecklist(request):
    if request.method == 'GET':
        return render(request, 'disasterchecklist.html')
    if request.method == 'POST':
        return render(request, 'home.html')

def logout(request):
    del request.session["user_email"]
    return render(request,'login.html')