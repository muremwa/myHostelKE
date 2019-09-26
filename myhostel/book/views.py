from django.views import generic, View
from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.urls import reverse_lazy
from django.http import Http404
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Hostel, Room, Booking
from .forms import BookRoomForm

import re


# noinspection PyUnresolvedReferences
class Retriever:
    def retrieve_school(self):
        try:
            school = self.request.session['school']
        except KeyError:
            self.request.session['school'] = None
            school = self.request.session['school']
        return school

    def retrieve_cookie(self):
        try:
            cookie = self.request.session['cookie']
        except KeyError:
            self.request.session['cookie'] = False
            cookie = self.request.session['cookie']
        return cookie


class Home(generic.TemplateView, Retriever):
    template_name = "home/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['school'] = self.retrieve_school()
        context['cookie'] = self.retrieve_cookie()
        return context


class Index(generic.ListView, Retriever):
    model = Hostel
    context_object_name = 'hostels'
    paginate_by = 12

    def get_queryset(self):
        school = self.retrieve_school()
        if school:
            query_set = Hostel.objects.filter(institution=school)
        else:
            query_set = Hostel.objects.all()
        return query_set.filter(available_rooms__gt=0).order_by('-available_rooms')

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
        context['cookie'] = self.retrieve_cookie()
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
        context['cookie'] = self.retrieve_cookie()
        return context


class RoomDetail(View, Retriever):
    def get(self, request, *args, **kwargs):
        room = get_object_or_404(Room, room_number=kwargs['room_number'])

        return render(request, 'book/room_detail.html', {
            'room': room,
            'school': self.retrieve_school(),
            'cookie': self.retrieve_cookie(),
        })


class RoomBooking(View, Retriever):
    template = 'book/now.html'
    form = BookRoomForm

    def get(self, request, **kwargs):
        room = get_object_or_404(Room, room_number=kwargs['room_number'])

        if not room.available:
            raise Http404

        return render(request, self.template, {
            'cookie': self.retrieve_cookie(),
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
                room.hostel.decrement_room_type(room.house_type)
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
            'cookie': self.retrieve_cookie(),
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
        context['cookie'] = self.retrieve_cookie()
        return context


# booking list
class BookingList(generic.ListView, Retriever):
    model = Booking
    template_name = 'book/bookings_list.html'
    context_object_name = 'bookings'
    paginate_by = 10

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise Http404
        else:
            return super().get(request, args, kwargs)

    def get_queryset(self):
        return Booking.objects.all().order_by('cleared')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['school'] = self.retrieve_school()
        context['cookie'] = self.retrieve_cookie()
        return context


# booking detail
class BookingDetail(generic.DetailView, Retriever):
    model = Booking
    template_name = "book/booking.html"
    context_object_name = 'booking'

    def get(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise Http404
        else:
            return super().get(request, args, kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['school'] = self.retrieve_school()
        context['cookie'] = self.retrieve_cookie()
        return context

    @staticmethod
    def post(request, *args, **kwargs):
        if not request.user.is_staff:
            raise Http404
        else:
            booking = get_object_or_404(Booking, pk=kwargs['pk'])
            booking.clear()
            messages.add_message(request, messages.INFO, 'Booking cleared')
            return redirect(reverse('booking-list'))


class BookingDelete(generic.DeleteView, Retriever):
    model = Booking
    success_url = reverse_lazy('booking-list')
    template_name = 'book/booking_confirm_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['school'] = self.retrieve_school()
        context['cookie'] = self.retrieve_cookie()
        return context


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

        return results.filter(available_rooms__gt=0).order_by('-available_rooms')

    @staticmethod
    def price_search(range_of_price, school, **kwargs):
        # split the query term eg '4000-8000' as [4000, 8000] and search the price range of the hostels that
        # have price ranges between the two. Hostel class has a method to split its price range
        hostels = Hostel.objects.filter(available_rooms__gt=0).order_by('-available_rooms')
        if school:
            hostels = hostels.filter(institution=school)
        res = []
        if kwargs['below']:
            for hostel in hostels:
                r = hostel.get_prices()
                try:
                    new_pr_range = int(range_of_price)
                except ValueError:
                    return res

                if new_pr_range >= r[0] and r[-1] >= new_pr_range:
                    res.append(hostel)
        else:
            try:
                from_ = int(range_of_price.split("-")[0])
                to_ = int(range_of_price.split("-")[-1])
            except ValueError:
                return res

            for hostel in hostels:
                r = hostel.get_prices()
                if r[0] >= from_ and r[-1] <= to_:
                    res.append(hostel)

        return res

    def advanced_search(self, query, school):
        query = query.split(":")
        field = query[0].upper()
        look_up = query[-1]
        term = None
        results = []

        price = ["PRICE", "RENT", "MONTHLY", "BELOW"]
        institution = ["UNIVERSITY", "CAMPUS", "SCHOOL", "COLLEGE", "INSTITUTION", "VARSITY", "AT"]
        location = ["PLACE", "IN", "WHERE", "LOCATED"]
        house_types = ["BEDROOM", ]
        one_room = ["ONE", "1"]
        two_bedroom = ["TWO", "2"]
        bed_sitter = ["BS", "BEDSITTER"]

        if field in price:
            # price searches
            below = False
            term = 'price'
            if field == price[-1]:
                below = True
            results = self.price_search(look_up, school, below=below)

        elif field in institution:
            # school search
            term = 'institution'
            results = Hostel.objects.filter(available_rooms__gt=0).filter(institution__icontains=look_up).order_by('-available_rooms')

        elif field in location:
            # location search
            term = 'location'
            results = Hostel.objects.filter(available_rooms__gt=0).filter(location__icontains=look_up).order_by('-available_rooms')
            if school:
                results = results.filter(institution=school)

        elif field in house_types:
            # house types
            look_up = look_up.upper()
            term = 'house_type'

            if look_up in one_room:
                look_up = "One Bedroom"
                results = Hostel.objects.all().filter(one__gt=0).order_by('-one')

            elif look_up in two_bedroom:
                look_up = "Two Bedroom"
                results = Hostel.objects.all().filter(two__gt=0).order_by('-two')

            elif look_up in bed_sitter:
                look_up = "Bedsitter"
                results = Hostel.objects.all().filter(bs__gt=0).order_by('-bs')

            elif look_up.upper() == "SINGLE" or look_up == "SINGLE ROOM":
                look_up = "Single Room"
                results = Hostel.objects.all().filter(sr__gt=0).order_by('-sr')

            else:
                # if none defaults to basic search
                results = []

            if school:
                results = results.filter(institution__icontains=school)

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

        try:
            count = results.count()
        except TypeError:
            count = len(results)

        # pagination
        page = self.request.GET.get('page', 1)
        paginator = Paginator(results, 10)

        try:
            results = paginator.page(page)
        except PageNotAnInteger:
            results = paginator.page(1)
        except EmptyPage:
            results = paginator.page(paginator.num_pages)

        return render(self.request, self.template_name, {
            'school': school,
            'query': query,
            'results': results,
            'advanced': ad_search,
            'advanced_field': ad_search_term,
            'advanced_lookup': ad_search_term_l,
            'count_results': count,
            'cookie': self.retrieve_cookie(),
        })
