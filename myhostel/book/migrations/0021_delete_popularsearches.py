# Generated by Django 2.1.5 on 2019-03-03 13:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0020_auto_20190222_1141'),
    ]

    operations = [
        migrations.DeleteModel(
            name='PopularSearches',
        ),
    ]