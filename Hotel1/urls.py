from  django.urls import path
from . import views
from .views import IndexView,AboutView,ContactView,RoomView,GalleryView,BlogView,RegisterView,LoginView,LogoutView,RoomDetailsView,BookingListView,BookingCreateView,BookingDetailView,BookingDeleteView,BookingConfirmationView,PaymentView,ProcessPaymentView,ElamentsView


urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Room URLs
    path('room/', RoomView.as_view(), name='rooms'),
    path('room/<int:id>/', RoomDetailsView.as_view(), name='room_details'),

    # Booking URLs
    path('bookings/', BookingListView.as_view(), name='booking_list'),  # List all bookings
    path('bookings/new/', BookingCreateView.as_view(), name='booking_create'),  # Create a new booking
    path('bookings/<int:pk>/', BookingDetailView.as_view(), name='booking_detail'),  # View booking details
    path('bookings/<int:pk>/delete/', BookingDeleteView.as_view(), name='booking_delete'),  # Delete a booking

    path('bookings/confirmation/<int:booking_id>/', BookingConfirmationView.as_view(), name='booking_confirmation'),

    path('payment/<int:booking_id>/', PaymentView.as_view(), name='booking_payment'),
    path('process-payment/<int:booking_id>/', ProcessPaymentView.as_view(), name='process_payment'),

    path('elements/', ElamentsView.as_view(), name='elements'),





    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('gallery/', GalleryView.as_view(), name='gallery'),
    path('blog/', BlogView.as_view(), name='blog'),



]