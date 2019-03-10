from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.core.validators import ValidationError

import re


def name_image(fullname, master, slug_of_master):
    try:
        fullname = fullname.split(".")
    except AttributeError:
        return
    new_name = '{}_{}'.format(master, slug_of_master)
    return "{}.{}".format(new_name, fullname[-1])


def sixteen_by_nine(width, height):
    lane = width*9
    lane = int(lane/16)
    if lane == int(height):
        return True
    else:
        return False


# hostel compound
class Hostel(models.Model):
    name = models.CharField(max_length=400, help_text='Preferred name of the premises')
    slug = models.SlugField(blank=True)
    location = models.CharField(max_length=400, help_text='Where is it found')
    institution = models.CharField(
        max_length=400,
        help_text='Always mention what Campus ie. Kisii University Main Campus'
    )
    available_rooms = models.IntegerField(default=0)
    all_rooms = models.IntegerField(blank=True, null=True)
    distance_from_admin = models.IntegerField(help_text='How far is it from the administration building')
    water = models.BooleanField(default=False, help_text='Is there free water?')
    electricity = models.BooleanField(default=False, help_text='Is there free power?')
    price_range = models.CharField(
        max_length=300,
        blank=True,
        help_text='Enter price range in the following format \'KSH 4500 - KSH 6000\''
    )
    views = models.IntegerField(default=0)
    objects = models.Manager()

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return '{} at {}'.format(self.name, self.institution)

    def clean(self):
        # the price range should be in the correct format
        if not re.search(r'KSH\s\d*\s-\sKSH\s\d*', str(self.price_range)):
            raise ValidationError(_('Please use the correct format for price range as described.'))

        # ranges should make sense
        ranges = str(self.price_range).split(" ")
        if ranges[1] > ranges[-1]:
            raise ValidationError(_("The range starts from lowest to highest"))

        return super().clean()

    def save(self, *args, **kwargs):
        self.slug = slugify(str(self.name))
        return super().save(args, kwargs)

    def delete(self, *args, **kwargs):
        # delete all images once the hostel is deleted
        images = self.hostelimage_set.all()
        for image in images:
            image.file.delete()
            print('deleted {}'.format(image.file))
        return super().delete()

    def get_main_image(self):
        try:
            img = self.hostelimage_set.filter(is_main=True)[0].file.url
        except IndexError:
            img = '/media/hostel/default_hostel.jpg'
        return img

    def get_absolute_url(self):
        return reverse('book:hostel', args=[str(self.slug)])

    def get_prices(self):
        res = str(self.price_range).split(" ")
        res_ = []
        for item in res:
            if item.isdigit():
                res_.append(item)
        return res_


# rooms
class Room(models.Model):
    house_types = (('1B', 'One Bedroom'), ('2B', 'Two Bedroom'), ('BS', 'Bedsitter'), ('SR', 'Single Room'))

    room_number = models.CharField(max_length=20, blank=True, null=True, unique=True)
    price = models.PositiveIntegerField()
    house_type = models.CharField(max_length=2, choices=house_types)
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE)
    available = models.BooleanField(default=True)
    tallied = models.BooleanField(default=False)
    objects = models.Manager()

    def __str__(self):
        return 'Room number {} a {} from {}'.format(self.room_number, self.house_type, self.hostel)

    def clean(self):
        # price should not be lower or higher than price range
        # noinspection PyUnresolvedReferences
        hostel_range = self.hostel.get_prices()
        # noinspection PyTypeChecker
        if self.price < int(hostel_range[0]) or self.price > int(hostel_range[-1]):
            raise ValidationError(_(
                "Ensure price is within the price range of the \"{}\" that is between {} and {}".format(
                    self.hostel.name,
                    hostel_range[0],
                    hostel_range[-1]
                )
            ))

        return super().clean()

    def save(self, *args, **kwargs):
        if not self.tallied:
            self.hostel.available_rooms += 1
            self.hostel.save()
            self.tallied = True
        else:
            if self.available:
                self.hostel.available_rooms += 1
                self.hostel.save()
        return super().save(args, kwargs)

    def delete(self, *args, **kwargs):
        # delete all images once the room is deleted
        images = self.roomimage_set.all()
        self.hostel.available_rooms -= 1
        for image in images:
            image.file.delete()
            print('deleted {}'.format(image.file))
        return super().delete()

    def get_main_image(self):
        try:
            img = self.roomimage_set.filter(is_main=True)[0].file.url
        except IndexError:
            img = '/media/rooms/default_room.png'
        return img

    def get_house_type(self):
        type_ = self.house_type
        if type_ == self.house_types[0][0]:
            return self.house_types[0][-1]
        elif type_ == self.house_types[1][0]:
            return self.house_types[1][-1]
        elif type_ == self.house_types[2][0]:
            return self.house_types[2][-1]
        elif type_ == self.house_types[3][0]:
            return self.house_types[3][-1]

    def get_absolute_url(self):
        return reverse('book:room', kwargs={'slug': str(self.hostel.slug), 'room_number': str(self.room_number)})


class RoomImage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    file = models.ImageField(upload_to='rooms/', help_text="PLEASE CROP TO 16:9")
    is_main = models.BooleanField(default=False, help_text="PLEASE MARK ONE AS MAIN!!!!")
    objects = models.Manager()

    def __str__(self):
        return 'For {}'.format(self.room)

    def save(self, *args, **kwargs):
        # noinspection PyUnresolvedReferences
        self.file.name = name_image(self.file.name, 'room', self.room.room_number)
        return super().save()

    def delete(self, *args, **kwargs):
        self.file.delete()
        return super().delete()

    def clean(self):
        # image to be 16:9
        # noinspection PyUnresolvedReferences
        if not sixteen_by_nine(self.file.width, self.file.height):
            raise ValidationError(_('Image is not 16:9 please crop it'))

        return super().clean()


class HostelImage(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE)
    file = models.ImageField(upload_to='hostel/', help_text="PLEASE CROP TO 16:9")
    is_main = models.BooleanField(default=False, help_text="PLEASE MARK ONE AS MAIN!!!!")
    objects = models.Manager()

    def __str__(self):
        return 'For {}'.format(self.hostel)

    def save(self, *args, **kwargs):
        self.file.name = name_image(self.file.name, 'hostel', self.hostel.slug)
        return super().save()

    def delete(self, *args, **kwargs):
        self.file.delete()
        return super().delete()

    def clean(self):
        # image to be 16:9
        # noinspection PyUnresolvedReferences
        if not sixteen_by_nine(self.file.width, self.file.height):
            raise ValidationError(_('Image is not 16:9 please crop it'))

        return super().clean()


# bookings
class Booking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, help_text='Enter your preferred name')
    phone_number = models.CharField(max_length=10, help_text='Enter phone number')
    date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    objects = models.Manager()

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return 'order by {} for {}'.format(self.name, self.room)

    def delete(self, using=None, keep_parents=False):
        self.room.available = True
        self.room.save()
        return super().delete()
