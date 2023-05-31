from django.shortcuts import render

# Create your views here.


def home(request):

    return render(request, 'landing/index.html', {})


def about(request):

    return render(request, 'landing/about.html', {})


def pricing(request):

    return render(request, 'landing/pricing.html', {})
