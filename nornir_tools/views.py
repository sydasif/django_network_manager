from django.shortcuts import render


def nornir_home(request):
    return render(request, "nornir_tools/index.html")
