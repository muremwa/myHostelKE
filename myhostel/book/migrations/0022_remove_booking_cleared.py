# Generated by Django 2.1.5 on 2019-03-10 06:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0021_delete_popularsearches'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='cleared',
        ),
    ]
