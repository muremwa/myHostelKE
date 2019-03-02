from django.shortcuts import render, redirect, reverse
from book.models import Hostel


def add_hostel(request):
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

        return render(request, 'action/specify.html', {
            'schools': schools,
            'school': school,
        })