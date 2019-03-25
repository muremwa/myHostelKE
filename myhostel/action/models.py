from django.db import models
from django.utils.text import slugify
from django.shortcuts import reverse


class PopularSearches(models.Model):
    term = models.TextField()
    count = models.IntegerField(default=0)

    def __str__(self):
        return "{} searched {} times".format(self.term, self.count)


class Faq(models.Model):
    question = models.CharField(max_length=400, unique=True)
    response = models.TextField(help_text="Enter a detailed explanation")
    slug = models.SlugField(unique=True)
    publish = models.BooleanField(default=False)
    objects = models.Manager()

    def __str__(self):
        return self.question

    def save(self, *args, **kwargs):
        self.slug = slugify(self.question)
        return super().save()

    def get_absolute_url(self):
        return reverse('help:faq', args=[str(self.slug)])
