from django.urls import path 
from  . import views

urlpatterns = [
	
    path("", views.mainhome, name="mainhome"),
	path("login/", views.index, name="ShopHome"),
	path("home/", views.index, name="ShopHome"),
    path("about/", views.about, name="AboutUs"),
	path("checkout/", views.checkout, name="Checkout"),
   
    path("contact/", views.contact, name="ContactUs"),
    path("tracker/", views.tracker, name="TrackingStatus"),
    path("search/", views.search, name="Search"),
    path("products/<int:myid>", views.productView, name="ProductView"),
    
    path("handlerequest/", views.handlerequest, name="HandleRequest"),
	path("signup/",views.Signup.as_view(),name="signup"),
    path('verify/',views.verify.as_view(),name="verify"),
    path("login/",views.Login1.as_view(),name="login"),
	path("logout/",views.handleLogout,name='handleLogout'),

]
