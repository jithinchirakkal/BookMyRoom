from django.shortcuts import render,redirect,get_object_or_404
from django.views import View
from .forms import CustomUserCreationForm,SignInForm,BookingForm
from .models import UserProfile,Room,Booking
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from datetime import datetime



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

class BookingCreateView(View):
    def get(self, request):
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
            booking.save()
            return redirect('booking_list')  # Redirect to a success page
        return render(request, 'booking_form.html', {'form': form})
        
class BookingListView(View):
    def get(self, request):
        bookings = Booking.objects.filter(user=request.user)  # Limit bookings to the logged-in user
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
    



        
