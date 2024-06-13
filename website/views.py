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
                return render(request,'login.html',{'msg':'Enter Correct Password','tag':'danger'})
        except Exception:
            return render(request,'login.html',{'msg':'Enter Correct Email','tag':'danger'})
def signup(request):
    if request.method == 'GET':
        return render(request,'signup.html')
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            email = request.POST.get('email')
            password = request.POST.get('password')
            mobile = request.POST.get('mobile')
            #print(name,email,password,mobile)
            user = Users()
            user.name = name
            user.email = email
            user.password = password
            user.mobile = mobile
            user.save()
            return render(request, 'familyinfo.html')
            #return render(request,'signup.html',{'msg':'Successfully Signup','tag':'success'})
        except Exception:
            return render(request,'signup.html',{'msg':'Error on Signup','tag':'danger'})

def familyinfo(request):
    return render(request, 'profile.html')

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
        mobile = request.POST.get('mobile')
        user = Users.objects.get(id=id)
        user.name = name
        user.password = password
        user.mobile = mobile
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
        return render(request, 'disasterchecklist.html')

def disasterchecklist(request):
    if request.method == 'GET':
        return render(request, 'disasterchecklist.html')
    if request.method == 'POST':
        return render(request, 'home.html')

def logout(request):
    del request.session["user_email"]
    return render(request,'login.html')