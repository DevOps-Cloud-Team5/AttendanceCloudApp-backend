from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, Http404
import os, re

#https://docs.djangoproject.com/en/5.0/ref/models/database-functions/
from django.contrib.auth import authenticate,login

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from django.contrib.auth.models import User

# from rest_framework.authentication import SessionAuthentication, BasicAuthentication
# from rest_framework.permissions import IsAuthenticated
from db_model import MyModel


__ROOT__ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def test(request):
    return JsonResponse({"data": "test"})



def log_auth(request):
    

    #request the token
    #check it
    #then retrieve the data
    authentication_classes = [authentication.TokenAuthentication]
    cur_username = request.data.get('username')
    cur_password = request.data.get('password')

    my_object = MyModel.objects.get(username = cur_username)
    username, password = my_object.username, my_object.password
    # user = authenticate(request, username=cur_username, password=cur_password)
    if cur_username == username:
        # login(request, user)
        # Change this later: Redirect to a success page.
        if cur_password == password:
            return JsonResponse('Success')
        else:
            return JsonResponse('Credentials are wrong. Go away.')
        
    else:
        # Return an 'invalid login' error message.
        #this as well
        return JsonResponse("User doesn't exist. Go away.")




