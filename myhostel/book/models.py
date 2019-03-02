from django.db import models
from django.utils.text import slugify
from django.urls import reverse


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

    def save(self, *args, **kwargs):
        self.slug = slugify(str(self.name))
        return super().save(args, kwargs)

    def get_main_image(self):
        return self.hostelimage_set.filter(is_main=True)[0]

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

    def get_absolute_url(self):
        return reverse('book:room', kwargs={'slug': str(self.hostel.slug), 'room_number':str(self.room_number)})


class RoomImage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    file = models.ImageField(upload_to='rooms/', help_text="PLEASE CROP TO 16:9")
    is_main = models.BooleanField(default=False, help_text="PLEASE MARK ONE AS MAIN!!!!")

    def __str__(self):
        return 'For {}'.format(self.room)


class HostelImage(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE)
    file = models.ImageField(upload_to='hostel/', help_text="PLEASE CROP TO 16:9")
    is_main = models.BooleanField(default=False, help_text="PLEASE MARK ONE AS MAIN!!!!")
    objects = models.Manager()

    def __str__(self):
        return 'For {}'.format(self.hostel)


# bookings
class Booking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, help_text='Enter your preferred name')
    phone_number = models.CharField(max_length=10, help_text='Enter phone number')
    cleared = models.BooleanField(default=False)
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
