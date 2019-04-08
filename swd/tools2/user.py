from django.contrib.auth.models import User
from django.shortcuts import render
from django.http import HttpResponse
from main.models import *
from .dev_info import users

def index(request):
    for name,username in users:
        password = User.objects.make_random_password()
        try:
            user = User.objects.create_user(username,"default@default.com",password)
            user.is_active = True;
            user.save()
        except:
            print("(Fail Username)")
        
        try:
            user = User.objects.get(username = username)
            profile = Student.objects.create(user=user, name=name)
            profile.save()
        except Exception as e:
            print('Fail (Profile)')
            print(e)

    return HttpResponse("Done")
