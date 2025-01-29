from django.shortcuts import render,redirect,get_object_or_404
from django.views import View
from .forms import CustomUserCreationForm,SignInForm,BookingForm,RoomForm
from .models import UserProfile,Room,Booking,Transaction
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from datetime import datetime
from django.http import JsonResponse
from paypalrestsdk import Payment  #import the paypal sdk
from django.conf import settings
from decimal import Decimal
import paypalrestsdk
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User



from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator






# Create your views here.

class IndexView(View):
    def get(self, request):
        room = Room.objects.filter(is_available=True)
        return render(request, 'index.html', {'rooms': room})
    
class AboutView(View):
    def get(self, request):
        return render(request, 'about.html')
    
class ContactView(View):
    def get(self, request):
        return render(request, 'contact.html')
    
class ElamentsView(View):
    def get(self, request):
        return render(request, 'elements.html')
    
class RoomView(View):
    def get(self, request):
        arrival_date = request.GET.get('arrival_date')
        departure_date = request.GET.get('departure_date')
        no_of_guests = request.GET.get('no_of_guests')

        # print(f"Arrival Date: {arrival_date}")


        # Parse the dates if present
        # if arrival_date:
        #     try:
        #         arrival_date = datetime.strptime(arrival_date, '%Y-%m-%d')
        #     except ValueError:
        #         pass  

        # if departure_date:
        #     try:
        #         departure_date = datetime.strptime(departure_date, '%Y-%m-%d')
        #     except ValueError:
        #         pass 

        # Filter rooms by availability
        room = Room.objects.filter(is_available=True)

        # Filter based on number of guests if provided
        # if on_of_guests:
        #     room = room.filter(max_guests__gte=int(on_of_guests))

        # Optionally filter rooms by availability dates
        # if arrival_date and departure_date:
        #     room = room.filter(available_from__lte=arrival_date, available_until__gte=departure_date)

        return render(request, 'accomodation.html', {
            'rooms': room,
            'arrival_date': arrival_date,
            'departure_date': departure_date,
            'no_of_guests': no_of_guests
        })
     
class RoomDetailsView(View):
    def get (self, request, id):
        instance = get_object_or_404(Room,id=id)
        return render(request,'room_details.html',{'instance':instance})

class BookingCreateView(LoginRequiredMixin, View):

    # Redirect non-logged-in users to the login page
    login_url = '/login/'
    redirect_field_name = 'next'

    def get(self, request):

        if not request.user.is_authenticated:
            messages.error(request, 'You must be logged in to book a room.')
            return redirect('self.login_url')
        
        #get query parameter
        room_id = request.GET.get('room_id')
        arrival_date = request.GET.get('arrival_date')
        departure_date = request.GET.get('departure_date')
        no_of_guests = request.GET.get('no_of_guests')

        # Get the room id from the query parameter
        room = get_object_or_404(Room,id=room_id) if room_id else None
        # room_id = request.GET.get('room_id')
        # if room_id:
        #     room = get_object_or_404(Room, id=room_id) # Get the room object
        # else:
        #     room = None

        # initial_data = {'room': room, 'check_in': arrival_date, 'check_out': departure_date, 'guests': no_of_guests}
        # form = BookingForm(initial=initial_data)
        # return render(request, 'booking_form.html', {'form': form, 'room': room})

        initial_data = {'room':room}
        if arrival_date:
            try:
                initial_data['check_in'] = datetime.strptime(arrival_date, '%Y-%m-%d')
                
            except ValueError:
                pass
        if departure_date:
            try:
                initial_data['check_out'] = datetime.strptime(departure_date, '%Y-%m-%d')
            except ValueError:
                pass
        if no_of_guests:
            try:
                initial_data['no_of_guests'] = int(no_of_guests)
            except ValueError:
                pass
        

        # Create the booking form
        form = BookingForm(initial=initial_data) # pre-fill the form if a room is specified
        return render(request, 'booking_form.html', {'form': form, 'room': room})

    def post(self, request):
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user  # Automatically assign the logged-in user
            
            # Calculate the total price
            booking.total_price = booking.room.price_per_night * (booking.check_out - booking.check_in).days

            # Check if the room is available
            room = booking.room
            if room.no_of_rooms <= 0:
                messages.error(request, 'Sorry, no rooms available.')
                return render(request, 'booking_form.html', {'form': form, 'room': room})
            
            #Decrement the number of rooms available
            room.no_of_rooms -= 1
            room.save()
            
            # Save the booking
            booking.save()

            return redirect('booking_confirmation',booking_id=booking.id)  # Redirect to a success page
        return render(request, 'booking_form.html', {'form': form})
    
class BookingConfirmationView(View):
    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)
        return render(request, 'booking_confirmation.html', {'booking': booking})
        
class BookingListView(LoginRequiredMixin, View):
    def get(self, request):
        bookings = Booking.objects.filter(user=request.user).order_by('-created_at')  # Limit bookings to the logged-in user
        return render(request, 'booking_list.html', {'bookings': bookings})
    
class BookingDeleteView(View):
    def get(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk, user=request.user)
        booking.delete()
        return redirect('booking_list')
    
class BookingDetailView(View):
    def get(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk, user=request.user)
        return render(request, 'booking_detail.html', {'booking': booking})
    
class PaymentView(View):
    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)
        return render(request, 'payment.html', {'booking': booking})
    
paypalrestsdk.configure({
    'mode': settings.PAYPAL_MODE,  # sandbox or live
    'client_id': settings.PAYPAL_CLIENT_ID,
    'client_secret': settings.PAYPAL_CLIENT_SECRET,
})


class ProcessPaymentView(View):

    def post(self, request, booking_id):
        # Fetch the booking object
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)

        # Create PayPal payment object
        payment = Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": request.build_absolute_uri('/payment-success/'),
                "cancel_url": request.build_absolute_uri('/payment-cancel/')
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": booking.room.name,
                        "sku": str(booking.id),
                        "price": f"{Decimal(booking.total_price):.2f}",
                        "currency": "USD",
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": f"{Decimal(booking.total_price):.2f}",
                    "currency": "USD"
                },
                "description": f"Purchase room: {booking.room.name}"
            }]
        })

        # Attempt to create the payment
        try:
            if payment.create():
                for link in payment.links:
                    if link.rel == "approval_url":
                        return redirect(link.href)
            else:
                return render(request, 'payment_cancel.html', {'error': payment.error})
        except Exception as e:
            return render(request, 'payment_error.html', {'error': str(e)})



class PaymentSuccessView(View):
    def get(self, request):
        payment_id = request.GET.get('paymentId')
        payer_id = request.GET.get('PayerID')
        payment = paypalrestsdk.Payment.find(payment_id)

        if payment.execute({"payer_id": payer_id}):
            # Get the room ID from the transaction items
            booking_id = payment.transactions[0]['item_list']['items'][0]['sku']  # Assuming there's only one
            booking = get_object_or_404(Booking, id=booking_id)

            # Mark the booking as paid
            booking.is_paid = True
            booking.save()

            # Create a transaction
            Transaction.objects.create(
                user = request.user,
                booking = booking,
                amount = Decimal(booking.total_price),
                payment_status = 'Completed'
            )
            return render(request, 'payment_success.html', {'booking': booking})
        else:
            return render(request, 'payment_cancel.html', {'error': payment.error})
        
class PaymentCancelView(View):
    def get(self, request):
        return render(request, 'payment_cancel.html')


    
class GalleryView(View):
    def get(self, request):
        return render(request, 'gallery.html')
    
class BlogView(View):
    def get(self, request):
        return render(request, 'blog.html')
    
class RegisterView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, 'register.html', {'form': form})
    
    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            birth = form.cleaned_data.get('birth_date')
            phone = form.cleaned_data.get('phone')

            # Create and save the UserProfile instance
            ob = UserProfile()
            ob.user = user
            ob.birth_date = birth
            ob.phone = phone
            ob.save()
            msg="User Created Successfully"

            messages.success(request, 'User  Created Successfully')

            return redirect('login')

        return render(request, 'register.html', {'form': form})
    
class LoginView(View):
    def get(self, request):
        form = SignInForm()
        return render(request, 'login.html', {'form': form})
    
    def post(self, request):
        form = SignInForm(request,request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                request.session['username'] = username
                request.session['id'] = user.id
                # return redirect('index')
                if user.is_staff:
                    return redirect('admin_dashboard')
                else:
                    return redirect('index')
            else:
                messages.error(request, 'Invalid username or password')
        else:
            messages.error(request, 'Invalid form submission')

        return render(request, 'login.html', {'form': form})
    
class LogoutView(View):
    def get(self, request):
    # def get(self, request, *args, **kwargs):
        if 'id' in request.session:
            del request.session['id']
        logout(request)
        return redirect('login')
    



        


# Helper Decorator for Staff Users
def is_staff_user(user):
    return user.is_staff

# Admin Dashboard View (Staff Only)
@method_decorator(user_passes_test(is_staff_user), name='dispatch')
class AdminDashboardView(View):
    def get(self, request):
        bookings = Booking.objects.all()
        total_revenue = sum(booking.total_price for booking in bookings)
        pending_bookings = Booking.objects.filter(status='Pending').count()
        users = User.objects.filter(is_staff=False)
        rooms = Room.objects.all()
        return render(request, 'admin_dashboard.html',{
            'bookings': bookings,
            'total_revenue': total_revenue,
            'pending_bookings': pending_bookings,
            'users': users,
            'rooms': rooms
        })

# Manage Rooms View (Staff Only)
@method_decorator(user_passes_test(is_staff_user), name='dispatch')
class ManageRoomsView(View):
    def get(self, request):
        rooms = Room.objects.all()
        return render(request, 'manage_rooms.html', {'rooms': rooms})

# Manage Bookings View (Staff Only)
@method_decorator(user_passes_test(is_staff_user), name='dispatch')
class ManageBookingsView(View):
    def get(self, request):
        bookings = Booking.objects.all().order_by('-created_at')
        return render(request, 'manage_bookings.html', {'bookings': bookings})


@method_decorator(user_passes_test(is_staff_user), name='dispatch')
class UpdateBookingStatusView(View):
    def post(self, request, pk):
        # Get the booking instance by its ID
        booking = get_object_or_404(Booking, pk=pk)

        # Get the selected status from the form if the booking is not paid
        new_status = request.POST.get('status')
        
        # If the booking is paid, automatically set the status to 'confirmed'
        # if booking.is_paid:
        #     # Set the status to confirmed if it is paid
        #     if booking.status != 'confirmed':  # Only update if not already confirmed
        #         booking.status = 'confirmed'
        #         booking.save()
        #         messages.success(request, "Booking status automatically updated to 'Confirmed' because the booking is paid.")
        # else:
            
        # Only allow valid status options to be updated
        if new_status in ['pending', 'confirmed', 'cancelled']:
            booking.status = new_status
            booking.save()
            messages.success(request, f"Booking status updated to {booking.get_status_display()}.")
        else:
            messages.error(request, "Invalid status update.")

        # Redirect back to the booking management page
        return redirect('manage_bookings')





# @method_decorator(user_passes_test(is_staff_user), name='dispatch')
# class UpdateBookingStatusView(View):
#     def post(self, request, pk):
#         booking = get_object_or_404(Booking, pk=pk)
#         status = request.POST.get('status')
        
#         if status in ['pending', 'confirmed', 'cancelled']:  # Only allow valid status updates
#             booking.status = status
#             booking.save()
#             messages.success(request, f"Booking status updated to {status.capitalize()}.")
#         else:
#             messages.error(request, "Invalid status.")
        
#         return redirect('manage_bookings')
    
@method_decorator(user_passes_test(is_staff_user), name='dispatch')
class DeleteBookingView(View):
    def get(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        booking.delete()
        messages.success(request, 'Booking deleted successfully!')
        return redirect('manage_bookings')



class AddEditRoomView(View):
    def get(self, request, pk=None):
        room = get_object_or_404(Room, pk=pk) if pk else None
        form = RoomForm(instance=room)
        return render(request, 'add_edit_room.html', {'form': form, 'room': room})

    def post(self, request, pk=None):
        room = get_object_or_404(Room, pk=pk) if pk else None
        form = RoomForm(request.POST, request.FILES, instance=room)
        if form.is_valid():
            form.save()
            if room:
                messages.success(request, 'Room updated successfully!')
            else:
                messages.success(request, 'Room added successfully!')
            return redirect('manage_rooms')  # Redirect to the rooms management page
        return render(request, 'add_edit_room.html', {'form': form, 'room': room})


@method_decorator(user_passes_test(is_staff_user), name='dispatch')
class DeleteRoomView(View):
    def get(self, request, pk):
        print(f"Attempting to delete room with ID {pk}")
        room = get_object_or_404(Room, pk=pk)
        room.delete()
        messages.success(request, 'Room deleted successfully!')
        return redirect('manage_rooms')
