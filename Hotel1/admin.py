from django.contrib import admin
from .models import Room, Booking,UserProfile,Transaction

# Register your models here.

# admin.site.register(Room)
admin.site.register(Booking)
@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'room_type', 'price_per_night', 'is_available')
    list_filter = ('room_type', 'is_available')
    search_fields = ('name',)

admin.site.register(UserProfile)

admin.site.register(Transaction)



