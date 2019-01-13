from django.views import generic, View
from django.shortcuts import get_object_or_404, render, reverse, redirect
from django.http import Http404

from .models import Hostel, Room, Booking
from .forms import BookRoomForm


class Index(generic.ListView):
    model = Hostel
    context_object_name = 'hostels'


class HostelDetail(generic.DetailView):
    model = Hostel
    context_object_name = 'hostel'
    slug_url_kwarg = 'slug'

    def hostel_suggestions(self, hostel):
        suggestions = Hostel.objects.filter(
            institution__icontains=hostel.institution
        ).filter(
            available_rooms__gt=0
        ).exclude(
            id=hostel.id
        )
        return suggestions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hostel_suggestions'] = self.hostel_suggestions(context['hostel'])
        return context


class RoomDetail(View):
    def get(self, request, *args, **kwargs):
        room = get_object_or_404(Room, room_number=kwargs['room_number'])

        if room.available:
            return render(request, 'book/room_detail.html', {
                'room': room
            })
        else:
            raise Http404


class RoomBooking(View):
    template = 'book/now.html'
    form = BookRoomForm

    def get(self, request, **kwargs):
        room = get_object_or_404(Room, room_number=kwargs['room_number'])

        if not room.available:
            raise Http404

        return render(request, self.template, {
            'room': room,
            'form': self.form
        })

    def post(self, request, **kwargs):
        form = self.form(request.POST)
        room = get_object_or_404(Room, room_number=kwargs['room_number'])

        if form.is_valid():
            name = form.cleaned_data['name']
            number = form.cleaned_data['phone_number']

            if room.available:
                Booking.objects.create(
                    room=room,
                    name=name,
                    phone_number=number
                )
                room.available = False
                room.hostel.available_rooms -= 1
                room.hostel.save()
                room.save()
            else:
                raise Http404

        else:
            return render(request, self.template, {
                'form': form,
                'room': room
            })

        return render(request, 'book/success_booking.html', {'room': room})
