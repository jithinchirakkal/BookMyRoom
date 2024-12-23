from django.shortcuts import render,redirect
from django.views import View
from .forms import CustomUserCreationForm,SignInForm
from .models import UserProfile,Room,Booking
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout



# Create your views here.

class IndexView(View):
    def get(self, request):
        return render(request, 'index.html')
    
class AboutView(View):
    def get(self, request):
        return render(request, 'about.html')
    
class ContactView(View):
    def get(self, request):
        return render(request, 'contact.html')
    
# class RoomView(View):
#     def get(self, request):
#         return render(request, 'accomodation.html')
class RoomView(View):
    def get(self, request):
        room = Room.objects.filter(is_available=True)
        return render(request, 'accomodation.html', {'rooms': room})
    
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


        
