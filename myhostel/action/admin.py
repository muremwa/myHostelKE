from django.contrib import admin

from .models import Faq


class FaqAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Question', {'fields': ['question', ]}),
        ('Response', {'fields': ['response', ]})
    ]
    list_display = ['question']


admin.site.register(Faq, FaqAdmin)
