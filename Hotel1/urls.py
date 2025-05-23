from  django.urls import include, path
from . import views
# from paypal.standard.ipn.views import ipn
from .views import IndexView,AboutView,ContactView,RoomView,GalleryView,BlogView,RegisterView,LoginView,LogoutView,RoomDetailsView,BookingListView,BookingCreateView,BookingDetailView,BookingDeleteView,BookingConfirmationView,PaymentView,ProcessPaymentView,PaymentSuccessView,PaymentCancelView,ElamentsView


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
    path('payment-success/', PaymentSuccessView.as_view(), name='payment-success'),
    path('payment-cancel/', PaymentCancelView.as_view(), name='payment-cancel'),

    # admin side

    path('admin-dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),

    path('manage-rooms/', views.ManageRoomsView.as_view(), name='manage_rooms'),
    path('rooms/add/', views.AddEditRoomView.as_view(), name='add_room'),
    path('rooms/edit/<int:pk>/', views.AddEditRoomView.as_view(), name='edit_room'),
    path('rooms/delete/<int:pk>/', views.DeleteRoomView.as_view(), name='delete_room'),


    path('manage-bookings/', views.ManageBookingsView.as_view(), name='manage_bookings'),
    path('booking/update-status/<int:pk>/', views.UpdateBookingStatusView.as_view(), name='update_booking_status'),
    path('bookings/delete/<int:pk>/', views.DeleteBookingView.as_view(), name='delete_booking'),






    path('elements/', ElamentsView.as_view(), name='elements'),





    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('gallery/', GalleryView.as_view(), name='gallery'),
    path('blog/', BlogView.as_view(), name='blog'),



]