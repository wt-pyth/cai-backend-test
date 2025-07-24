from django.http import HttpResponse

def home(request):
    return HttpResponse("🚀 Django on Cloud Run is working!")
