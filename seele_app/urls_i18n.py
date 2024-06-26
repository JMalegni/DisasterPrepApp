from django.urls import path
from website import views

urlpatterns = [
    path('', views.home, name="home"),
    path('login/', views.login, name="login"),
    path('signup/', views.signup, name="signup"),
    path('familyinfo/', views.familyinfo, name="familyinfo"),
    path('profile/', views.profile, name="profile"),
    path('disasterprep/', views.disasterprep, name="disasterprep"),
    path('disasterchecklist/', views.disasterchecklist, name="disasterchecklist"),
    path('logout/', views.logout, name="logout"),
]
