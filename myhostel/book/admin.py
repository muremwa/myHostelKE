from django.contrib import admin
from .models import Room, Hostel, Booking, RoomImage, HostelImage


class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 4


class HostelImageInline(admin.TabularInline):
    model = HostelImage
    extra = 4


class RoomAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Room Details', {'fields': ['room_number', 'house_type']}),
        ('Info', {'fields': ['price', 'hostel', 'available']})
    ]

    list_display = ['room_number', 'hostel', 'house_type', 'price', 'available']
    list_filter = ['house_type',]
    search_fields = ['house_type', 'price', 'room_number', 'hostel']
    inlines = (RoomImageInline,)


class HostelAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Hostel Details', {'fields': ['name', 'location', 'institution', 'price_range']}),
        ('Info', {'fields': ['distance_from_admin', 'water', 'electricity']})
    ]
    list_display = ['name', 'institution', 'distance_from_admin']
    list_filter = ['institution',]
    search_fields = ['institution', 'location', 'name']
    inlines = (HostelImageInline,)


class BookingAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Customer Information', {'fields': ['name', 'phone_number']}),
        ('Order Details', {'fields': ['room']})
    ]
    list_display = ['name', 'phone_number', 'room']

admin.site.register(Room, RoomAdmin)
admin.site.register(Hostel, HostelAdmin)
admin.site.register(Booking, BookingAdmin)