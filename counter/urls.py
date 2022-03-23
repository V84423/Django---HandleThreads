from django.urls import path
from . import views

urlpatterns = [
        
        path('', views.dashboard, name='dashboard'),
        path('login/$msg', views.login, name='login'),
        path('logout/', views.logout, name='logout'),
        path('register/', views.register, name='register'),
        path('login/user', views.loginUser, name='loginUser'),
        path('register/user', views.registerUser, name='addUser'),


        path('shop/', views.shop, name='shop'),
        path('add/shop', views.addShop, name='addShop'),
        path('start/shop', views.startShop, name='startShop'),
        path('get/shop', views.getShop, name='getShop'),
        path('del/shop', views.delShop, name='delShop'),

        path('machine/', views.machine, name='machine'),
        path('get/machine', views.getMachine, name='getMachine'),

        path('unit/', views.unit, name='unit'),
        path('get/unit', views.getUnit, name='getUnit'),

        path('data/', views.data, name='data'),
        path('get/data', views.getData, name='getData'),

        path('start/scrap', views.startScrap, name='startScrap'),
        path('check/scrap', views.checkScrap, name='checkScrap'),

        path('database/Xserver', views.moveDatabase, name='moveDatabase'),
]
