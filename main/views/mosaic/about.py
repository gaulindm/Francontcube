from django.shortcuts import render

def about(request):
    return render(request, "main/mosaic/about.html")
