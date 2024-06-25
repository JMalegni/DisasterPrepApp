"""ecom URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from website.views import *
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',home,name="home"),
    # path('i18n/', include('django.conf.urls.i18n')),
    path('login/',login,name="login"),
    path('signup/',signup,name="signup"),
    path('familyinfo/',familyinfo,name="familyinfo"),
    path('profile/',profile,name="profile"),
    path('disasterprep/',disasterprep,name="disasterprep"),
    path('disasterchecklist/',disasterchecklist,name="disasterchecklist"),
    path('disasterposter/', disasterposter, name="disasterposter"),
    path('disasterposter/<int:user_id>/', disasterposter, name="disasterposter"),
    path('download/', download_poster, name='download_poster'),
    path('logout/',logout,name="logout"),
]

urlpatterns += i18n_patterns(
    path('', include('seele_app.urls_i18n')),
    path('i18n/', include('django.conf.urls.i18n')),
)