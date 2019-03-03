from django import forms

from .models import Bug, Feedback


class BugForm(forms.ModelForm):
    class Meta:
        model = Bug
        fields = ('report',)


class FeedBackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = '__all__'
