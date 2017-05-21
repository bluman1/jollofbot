import os
import re
import requests
import json
import random
from pprint import pprint
import googlemaps
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.http.response import HttpResponse
from django.http import JsonResponse
from django.http import QueryDict
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status

from jolllof.buy import * as buy
from jolllof.sell import * as sell

BUYER_ACCESS_TOKEN = os.environ.get('BUYER_ACCESS_TOKEN')
SELLER_ACCESS_TOKEN = os.environ.get('SELLER_ACCESS_TOKEN')

BUYER_CHALLENGE = os.environ.get('BUYER_CHALLENGE')
SELLER_CHALLENGE = os.environ.get('SELLER_CHALLENGE')

# Create your views here.

def show_landing(request):
    return HttpResponse()


@csrf_exempt
def buyer_subscribe(request):
    if request.method == 'GET':
        response = requests.post(
            'https://graph.facebook.com/v2.6/me/subscribed_apps?access_token=' + BUYER_ACCESS_TOKEN)
        pprint(response.json())
        return HttpResponse()


@csrf_exempt
def buyer_prep(request):
    buy.get_started_button()
    # c2c_persistent_menu()
    return HttpResponse()


@csrf_exempt
def buyer_webhook(request):
    if request.method == 'GET':
        if request.GET['hub.verify_token'] == BUYER_CHALLENGE:
            return HttpResponse(request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')
    elif request.method == 'POST':
        # Converts the text payload into a python dictionary
        incoming_message = json.loads(request.body.decode('utf-8'))



###################################################################################################


@csrf_exempt
def seller_subscribe(request):
    if request.method == 'GET':
        response = requests.post(
            'https://graph.facebook.com/v2.6/me/subscribed_apps?access_token=' + SELLER_ACCESS_TOKEN)
        pprint(response.json())
        return HttpResponse()


@csrf_exempt
def seller_prep(request):
    sell.get_started_button()
    # c2c_persistent_menu()
    return HttpResponse()


@csrf_exempt
def seller_webhook(request):
    if request.method == 'GET':
        if request.GET['hub.verify_token'] == SELLER_CHALLENGE:
            return HttpResponse(request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')
    elif request.method == 'POST':
        # Converts the text payload into a python dictionary
        incoming_message = json.loads(request.body.decode('utf-8'))