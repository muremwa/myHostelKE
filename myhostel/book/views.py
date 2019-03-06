from django.views import generic, View
from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.http import Http404
from django.utils.datastructures import MultiValueDictKeyError
from django.contrib import messages
from django.db.models import Q

from .models import Hostel, Room, Booking, HostelImage
from .forms import BookRoomForm, HostelForm, HostelImagesFormSet

import re


class Retriever:
    def retrieve_school(self):
        try:
            school = self.request.session['school']
        except KeyError:
            self.request.session['school'] = None
            school = self.request.session['school']
        return school


class Home(generic.TemplateView, Retriever):
    template_name = "home/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['school'] = self.retrieve_school()
        return context


class Index(generic.ListView, Retriever):
    model = Hostel
    context_object_name = 'hostels'

    def get_queryset(self):
        school = self.retrieve_school()
        if school:
            query_set = Hostel.objects.filter(institution=school)
        else:
            query_set = Hostel.objects.all()
        return query_set.order_by('-available_rooms')

    def popular_hostels(self):
        # gets all popular hostels according to views it has gathered
        return self.model.objects.order_by('-views').filter(views__gt=0)[:4]

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        # recent searches
        try:
            recent = self.request.session['recent_searches'][-5:]
        except KeyError:
            self.request.session['recent_searches'] = []
            recent = self.request.session['recent_searches'][-5:]

        context['school'] = self.retrieve_school()
        context['recent_searches'] = list(reversed(recent))
        context['popular'] = self.popular_hostels()
        return context


class HostelDetail(generic.DetailView, Retriever):
    model = Hostel
    context_object_name = 'hostel'
    slug_url_kwarg = 'slug'

    @staticmethod
    def hostel_suggestions(hostel):
        suggestions = Hostel.objects.filter(
            # suggest hostels from same school
            institution__icontains=hostel.institution
        ).filter(
            # all to have available rooms
            available_rooms__gt=0
        ).exclude(
            id=hostel.id
        )
        return suggestions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hostel_suggestions'] = self.hostel_suggestions(context['hostel'])

        # add a view to the hostel using sessions
        try:
            seen = self.request.session['hostels_seen']
        except KeyError:
            self.request.session['hostels_seen'] = []
            seen = self.request.session['hostels_seen']

        if context['hostel'].pk not in seen:
            seen.append(context['hostel'].pk)
            context['hostel'].views += 1
            self.request.session['seen'] = seen
        context['hostel'].save()
        context['school'] = self.retrieve_school()
        return context


class RoomDetail(View, Retriever):
    def get(self, request, *args, **kwargs):
        room = get_object_or_404(Room, room_number=kwargs['room_number'])

        # if room is booked it will return a 404 error
        if room.available:
            return render(request, 'book/room_detail.html', {
                'room': room,
                'school': self.retrieve_school()
            })
        else:
            raise Http404


class RoomBooking(View, Retriever):
    template = 'book/now.html'
    form = BookRoomForm

    def get(self, request, **kwargs):
        room = get_object_or_404(Room, room_number=kwargs['room_number'])

        if not room.available:
            raise Http404

        return render(request, self.template, {
            'school': self.retrieve_school(),
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
                # create a booking instance
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
        return render(request, 'book/success_booking.html', {
            'room': room,
            'school': self.retrieve_school(),
        })


# staff actions home
class StaffActions(generic.TemplateView, Retriever):
    template_name = 'book/staff.html'

    def get(self, request, *args, **kwargs):
        # non staff users are get a 404 error by this page
        if not self.request.user:
            raise Http404
        elif not self.request.user.is_staff:
            raise Http404
        else:
            return super().get(request, args, kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['school'] = self.retrieve_school()
        return context


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

    @staticmethod
    def save_hostel_images(hostel, images):
        # save images for a hostel
        for k, img in enumerate(images):

            # the first is the main image
            if k == 0:
                main = True
            else:
                main = False

            HostelImage.objects.create(
                hostel=hostel,
                file=img,
                is_main=main
            )

    def post(self, *args, **kwargs):
        hostel_form = self.hostel_form_class(self.request.POST, self.request.FILES)
        new_hostel = None
        images = []

        if hostel_form.is_valid():
            for i in range(5):
                # dump all images into a list that is sent to the image saving method
                try:
                    images.append(self.request.FILES['form-{}-hostel_image'.format(i)])
                except MultiValueDictKeyError:
                    break

            # always have an image for the hostel
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


# booking list
class BookingList(generic.ListView):
    model = Booking
    template_name = 'book/bookings_list.html'
    context_object_name = 'bookings'

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise Http404
        else:
            return super().get(request, args, kwargs)


# booking detail
class BookingDetail(generic.DetailView):
    model = Booking
    template_name = "book/booking.html"
    context_object_name = 'booking'

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise Http404
        else:
            return super().get(request, args, kwargs)

    @staticmethod
    def post(request, *args, **kwargs):
        if not request.user.is_staff:
            raise Http404
        else:
            booking = get_object_or_404(Booking, pk=kwargs['pk'])
            booking.delete()
            messages.add_message(request, messages.INFO, 'Booking cleared')
            return redirect(reverse('booking-list'))


# search action
class Search(generic.TemplateView, Retriever):
    template_name = 'book/search.html'

    @staticmethod
    def basic_search(query, school):
        # search in the name, school and location fields
        q_set = (
                Q(name__icontains=query) |
                Q(institution__icontains=query) |
                Q(location__icontains=query)
        )
        results = Hostel.objects.filter(q_set)

        if school:
            results = results.filter(institution__contains=school)

        return results.order_by('-available_rooms')

    @staticmethod
    def price_search(range_of_price, school):
        # split the query term eg '4000-8000' as [4000, 8000] and search the price range of the hostels that
        # have price ranges between the two. Hostel class has a method to split its price range
        hostels = Hostel.objects.filter(available_rooms__gt=0).order_by('-available_rooms')
        if school:
            hostels = hostels.filter(institution=school)
        res = []
        from_ = range_of_price.split("-")[0]
        to_ = range_of_price.split("-")[-1]

        for hostel in hostels:
            r = hostel.get_prices()
            if from_ >= r[0] and to_ <= r[-1]:
                res.append(hostel)

        return res

    @staticmethod
    def house_type_search(look, school):
        hostels = Hostel.objects.filter(available_rooms__gt=0)
        if school:
            hostels = hostels.filter(institution=school)
        res = {}

        for hostel in hostels:
            # increment this for each of "the room type" the hostel has.
            count_of_look = 0
            for room in hostel.room_set.all():
                if room.house_type == look:
                    count_of_look += 1

            # if a hostel has none of "the room type" it's not added
            if count_of_look:
                res[hostel] = count_of_look

        # sort the hostels according to the number of "the room type" each has
        res = dict(reversed(sorted(res.items(), key=lambda kv: kv[1])))

        return res

    def advanced_search(self, query, school):
        query = query.split(":")
        field = query[0].upper()
        look_up = query[-1]
        term = None
        results = []

        price = ["PRICE", "RENT", "MONTHLY"]
        institution = ["UNIVERSITY", "CAMPUS", "SCHOOL", "COLLEGE", "INSTITUTION", "VARSITY", "AT"]
        location = ["PLACE", "IN", "WHERE", "LOCATED"]
        house_types = ["BEDROOM", ]
        one_room = ["ONE", "1"]
        two_bedroom = ["TWO", "2"]
        bed_sitter = ["BS", "BEDSITTER"]

        if field in price:
            # price searches
            term = 'price'
            results = self.price_search(look_up, school)

        elif field in institution:
            # school search
            term = 'institution'
            results = Hostel.objects.filter(institution__icontains=look_up).order_by('-available_rooms')

        elif field in location:
            # location search
            term = 'location'
            results = Hostel.objects.filter(location__icontains=look_up).order_by('-available_rooms')
            if school:
                results = results.filter(institution=school)

        elif field in house_types:
            # house types
            look_up = look_up.upper()
            term = 'house_type'

            if look_up in one_room:
                look_up = "One Bedroom"
                results = self.house_type_search('1B', school)

            elif look_up in two_bedroom:
                look_up = "Two Bedroom"
                results = self.house_type_search('2B', school)

            elif look_up in bed_sitter:
                look_up = "Bedsitter"
                results = self.house_type_search('BS', school)

            elif look_up.upper() == "SINGLE" or look_up == "SINGLE ROOM":
                look_up = "Single Room"
                results = self.house_type_search('SR', school)

            else:
                # if none defaults to basic search
                results = self.basic_search(look_up, school)

        return {'results': results, 'term': term, 'look_up': look_up}

    def get(self, *args, **kwargs):
        query = self.request.GET['query']
        ad_search = False
        ad_search_term = None
        ad_search_term_l = None

        # retrieve previous searches
        try:
            recent = self.request.session['recent_searches']
        except KeyError:
            self.request.session['recent_searches'] = []
            recent = self.request.session['recent_searches']

        school = self.retrieve_school()

        # check if the search is advanced
        if re.search(r'\w+:\w+', query):
            if len(query.split(':')) == 2:
                ad_search = True
                temp = self.advanced_search(query, school)
                results = temp['results']
                ad_search_term = temp['term']
                ad_search_term_l = temp['look_up']
            else:
                results = self.basic_search(query, school)
        else:
            results = self.basic_search(query, school)

        # if the search has results it is added to session searches
        if results:
            if query in recent:
                recent.remove(query)
            recent.append(query)
            self.request.session['recent_searches'] = recent

        return render(self.request, self.template_name, {
            'school': school,
            'query': query,
            'results': results,
            'advanced': ad_search,
            'advanced_field': ad_search_term,
            'advanced_lookup': ad_search_term_l,
        })
