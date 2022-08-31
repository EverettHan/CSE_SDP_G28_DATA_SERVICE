"""webservice URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from distclassifier import views


urlpatterns = [
    path('admin/', admin.site.urls),
    # USER VIEWS
    path('createuser', views.CreateUserView.as_view()),
    path('getallusers', views.GetAllUsersView.as_view()),
    # Dataset VIEWS
    path('createdataset', views.CreateDatasetView.as_view()),
    # Model VIEWS
    # ClassificationRequest VIEWS
    path('classify', views.ClassifyView.as_view()),
    path('requestwork', views.RequestWork.as_view()),
    path('requestjobs', views.RequestJobs.as_view()),
    path('getimage', views.GetImage.as_view()),
    path('reportclassification', views.ReportClassification.as_view()),
    path('getresults', views.GetResults.as_view())
    # ClassificationResult VIEWS
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
