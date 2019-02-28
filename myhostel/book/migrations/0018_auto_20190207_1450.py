# Generated by Django 2.1.5 on 2019-02-07 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0017_hostel_all_rooms'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='cleared',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='hostel',
            name='available_rooms',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='hostel',
            name='distance_from_admin',
            field=models.IntegerField(help_text='How far is it from the administration building'),
        ),
        migrations.AlterField(
            model_name='hostel',
            name='electricity',
            field=models.BooleanField(default=False, help_text='Is there free power?'),
        ),
        migrations.AlterField(
            model_name='hostel',
            name='institution',
            field=models.CharField(help_text='Always mention what Campus ie. Kisii University Main Campus', max_length=400),
        ),
        migrations.AlterField(
            model_name='hostel',
            name='location',
            field=models.CharField(help_text='Where is it found', max_length=400),
        ),
        migrations.AlterField(
            model_name='hostel',
            name='name',
            field=models.CharField(help_text='Preferred name of the premises', max_length=400),
        ),
        migrations.AlterField(
            model_name='hostel',
            name='price_range',
            field=models.CharField(blank=True, help_text="Enter price range in the following format 'KSH 4500 - KSH 6000'", max_length=300),
        ),
        migrations.AlterField(
            model_name='hostel',
            name='water',
            field=models.BooleanField(default=False, help_text='Is there free water?'),
        ),
        migrations.AlterField(
            model_name='room',
            name='house_type',
            field=models.CharField(choices=[('1B', 'One Bedroom'), ('2B', 'Two Bedroom'), ('BS', 'Bedsitter'), ('SR', 'Single Room')], max_length=2),
        ),
    ]