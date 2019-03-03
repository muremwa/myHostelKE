from django.contrib import admin

from .models import Faq, Feedback, Bug


class FaqAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Question', {'fields': ['question', ]}),
        ('Response', {'fields': ['response', ]})
    ]
    list_display = ['question']


admin.site.register(Faq, FaqAdmin)


class FeedBackAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Info', {'fields': ['email', ]}),
        ('Feedback', {'fields': ['text']})
    ]
    list_display = ['email', 'date']


admin.site.register(Feedback, FeedBackAdmin)


class BugAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Info', {'fields': ['page', ]}),
        ('Bug Report', {'fields': ['report']})
    ]
    list_display = ['date']


admin.site.register(Bug, BugAdmin)
