from django.shortcuts import render, redirect, reverse
from django.views import generic
from django.http import Http404

from book.models import Hostel
from book.views import Retriever
from .models import Faq


def add_school(request):
    if request.method == "POST":
        school = request.POST['school']
        if school:
            request.session['school'] = school
        return redirect(reverse('book:index'))
    else:
        schools = []
        for hostel in Hostel.objects.all():
            if hostel.institution not in schools:
                schools.append(hostel.institution)

        try:
            school = request.session['school']
        except KeyError:
            request.session['school'] = None
            school = request.session['school']

        try:
            cookie = request.session['cookie']
        except KeyError:
            request.session['cookie'] = False
            cookie = request.session['cookie']

        return render(request, 'action/specify.html', {
            'schools': schools,
            'school': school,
            'cookie': cookie,
        })


def remove_school(request):
    request.session['school'] = None
    to = request.GET.get('next')
    if not to:
        to = '/'
    return redirect(to)


def accept_cookies(request):
    request.session['cookie'] = True
    to = request.GET.get('next')
    if not to:
        to = '/'
    return redirect(to)


# all frequently asked questions
class FaqList(generic.ListView, Retriever):
    model = Faq
    context_object_name = 'faqs'
    template_name = 'action/faq_list.html'
    paginate_by = 15

    def get_queryset(self):
        return Faq.objects.filter(publish=True)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        context['school'] = self.retrieve_school()
        context['cookie'] = self.retrieve_cookie()
        return context


# each faq
class FaqDetail(generic.DetailView, Retriever):
    model = Faq
    context_object_name = 'faq'
    template_name = 'action/faq.html'
    slug_url_kwarg = 'slug'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()
        # raise 404 if article is not published
        if not context['faq'].publish:
            raise Http404('The FAQ item you requested is not published yet')

        # add school and cookie to context
        context['school'] = self.retrieve_school()
        context['cookie'] = self.retrieve_cookie()
        return context
