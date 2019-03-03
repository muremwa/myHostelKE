from django.db import models
from django.utils.text import slugify
from django.shortcuts import reverse


class PopularSearches(models.Model):
    term = models.TextField()
    count = models.IntegerField(default=0)

    def __str__(self):
        return "{} searched {} times".format(self.term, self.count)


class Faq(models.Model):
    question = models.CharField(max_length=400)
    response = models.TextField(help_text="Enter a detailed explanation")
    slug = models.SlugField()
    objects = models.Manager()

    def __str__(self):
        return self.question

    def save(self, *args, **kwargs):
        self.slug = slugify(self.question)
        return super().save()

    def get_absolute_url(self):
        return reverse('help:faq', args=[str(self.slug)])


class Feedback(models.Model):
    text = models.TextField(help_text="Comment on your experience")
    email = models.EmailField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    class Meta:
        ordering = ('-date',)
        verbose_name_plural = "Feedback"

    def __str__(self):
        return "Feedback by {}".format(self.email)


class Bug(models.Model):
    report = models.TextField("Please enter a detailed explanation of the error that occurred")
    page = models.URLField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Bug report on {}".format(self.date)
