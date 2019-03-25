from django.contrib import admin

from .models import Faq


class FaqAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Question', {'fields': ['question', ]}),
        ('Response', {'fields': ['response', ]})
    ]
    list_display = ['question', 'publish']
    actions = ['publish',]

    def publish(self, request, queryset):
        queryset.update(publish=True)
        self.message_user(request, "Article(s) were published")


admin.site.register(Faq, FaqAdmin)
