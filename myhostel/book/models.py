from django.db import models
from django.utils.text import slugify


# hostel compound
class Hostel(models.Model):
    name = models.CharField(max_length=400)
    slug = models.SlugField(blank=True)
    location = models.CharField(max_length=400)
    institution = models.CharField(max_length=400)
    available_rooms = models.IntegerField()
    all_rooms = models.IntegerField(blank=True, null=True)
    distance_from_admin = models.IntegerField()
    water = models.BooleanField(default=False)
    electricity = models.BooleanField(default=False)
    price_range = models.CharField(max_length=300, blank=True)
    objects = models.Manager()

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return '{} at {}'.format(self.name, self.institution)

    def save(self, *args, **kwargs):
        self.slug = slugify(str(self.name))
        return super().save(args, kwargs)

    def get_main_image(self):
        return self.hostelimage_set.filter(is_main=True)[0]


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

    def get_main_image(self):
        return self.roomimage_set.filter(is_main=True)[0]

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


class RoomImage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    file = models.ImageField(upload_to='rooms/')
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return 'For {}'.format(self.room)


class HostelImage(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE)
    file = models.ImageField(upload_to='hostel/')
    is_main = models.BooleanField(default=False)

    def __str__(self):
        return 'For {}'.format(self.hostel)


# bookings
class Booking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, help_text='Enter your preferred name')
    phone_number = models.CharField(max_length=10, help_text='Enter phone number')
    objects = models.Manager()

    def __str__(self):
        return 'order by {} for {}'.format(self.name, self.room)

    def delete(self, using=None, keep_parents=False):
        self.room.available = True
        self.room.save()
        self.room.hostel.available_rooms += 1
        self.room.hostel.save()
        return super().delete()
