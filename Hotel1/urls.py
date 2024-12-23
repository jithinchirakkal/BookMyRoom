from  django.urls import path
from . import views
from .views import IndexView,AboutView,ContactView,RoomView,GalleryView,BlogView,RegisterView,LoginView,LogoutView


urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),



    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('room/', RoomView.as_view(), name='rooms'),
    path('gallery/', GalleryView.as_view(), name='gallery'),
    path('blog/', BlogView.as_view(), name='blog'),



]