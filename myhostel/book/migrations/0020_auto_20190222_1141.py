# Generated by Django 2.1.5 on 2019-02-22 08:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('book', '0019_booking_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='PopularSearches',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('term', models.TextField()),
                ('count', models.IntegerField(default=0)),
            ],
        ),
        migrations.AlterModelOptions(
            name='booking',
            options={'ordering': ['-date']},
        ),
        migrations.AddField(
            model_name='hostel',
            name='views',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='hostelimage',
            name='file',
            field=models.ImageField(help_text='PLEASE CROP TO 16:9', upload_to='hostel/'),
        ),
        migrations.AlterField(
            model_name='hostelimage',
            name='is_main',
            field=models.BooleanField(default=False, help_text='PLEASE MARK ONE AS MAIN!!!!'),
        ),
        migrations.AlterField(
            model_name='roomimage',
            name='file',
            field=models.ImageField(help_text='PLEASE CROP TO 16:9', upload_to='rooms/'),
        ),
        migrations.AlterField(
            model_name='roomimage',
            name='is_main',
            field=models.BooleanField(default=False, help_text='PLEASE MARK ONE AS MAIN!!!!'),
        ),
    ]
