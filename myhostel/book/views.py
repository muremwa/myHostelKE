from django.views import generic, View
from django.shortcuts import get_object_or_404, render, redirect
from django.http import Http404
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib import messages

from .models import Hostel, Room, Booking, HostelImage
from .forms import BookRoomForm, HostelForm, HostelImagesFormSet

import re


class Index(generic.ListView):
    model = Hostel
    context_object_name = 'hostels'


class HostelDetail(generic.DetailView):
    model = Hostel
    context_object_name = 'hostel'
    slug_url_kwarg = 'slug'

    @staticmethod
    def hostel_suggestions(hostel):
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


# staff actions home
class StaffActions(generic.TemplateView):
    template_name = 'book/staff.html'

    def get(self, request, *args, **kwargs):
        if not self.request.user:
            raise Http404
        elif not self.request.user.is_staff:
            raise Http404
        else:
            return super().get(request, args, kwargs)


# add hostel
class StaffAddHostel(View):
    template = 'book/add_hostel.html'
    hostel_form_class = HostelForm
    images_form_set = HostelImagesFormSet

    def get(self, *args, **kwargs):
        if not self.request.user:
            raise Http404
        elif not self.request.user.is_staff:
            raise Http404
        else:
            return render(self.request, self.template, {
                'form': self.hostel_form_class(initial={'price_range': 'KSH 0000 - KSH 0000'}),
                'images_form': self.images_form_set
            })

    def save_hostel_images(self, hostel, images):
        for k, img in enumerate(images):
            image = img

            # the first is the main image
            if k == 0:
                main = True
            else:
                main = False

            HostelImage.objects.create(
                hostel=hostel,
                file=image,
                is_main=main
            )

    def post(self, *args, **kwargs):
        hostel_form = self.hostel_form_class(self.request.POST, self.request.FILES)
        images_form = self.images_form_set(self.request.POST, self.request.FILES)
        new_hostel = None
        images = []

        if hostel_form.is_valid():
            for i in range(5):
                try:
                    images.append(self.request.FILES['form-{}-hostel_image'.format(i)])
                except MultiValueDictKeyError:
                    break

            if not any(images):
                messages.add_message(self.request, messages.WARNING, 'Please add at least one image')
                return render(self.request, self.template, {
                    'form': hostel_form,
                    'images_form': self.images_form_set
                })

            hostel_form.save()
            new_hostel = get_object_or_404(Hostel, name=hostel_form.cleaned_data['name'])
            self.save_hostel_images(new_hostel, images)

        return redirect(new_hostel.get_absolute_url())
