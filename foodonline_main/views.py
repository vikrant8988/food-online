from django.http import HttpResponse
from django.shortcuts import render
from django.contrib import messages

def home(request):
    messages.error(request, "Your action was successful!")  # Message added
    return render(request, 'home.html')