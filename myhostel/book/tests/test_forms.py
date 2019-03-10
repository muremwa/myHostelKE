from django.test import TestCase, tag
from django.urls import reverse

# noinspection PyUnresolvedReferences
from book.forms import BookRoomForm
# noinspection PyUnresolvedReferences
from book.models import Hostel, Room


@tag('book-form')
class BookFormTest(TestCase):
    def setUp(self):
        self.hostel = Hostel(
            name='The Crud',
            location='Uplands, Limuru, Kiambu',
            institution='St. Paul\'s University Main Campus',
            price_range='KSH 4500 - KSH 6000',
            distance_from_admin='5000',
            water=True,
            electricity=False
        )
        self.hostel.save()
        self.room = Room(
            room_number='cr-1',
            house_type='BS',
            price='5000',
            hostel=self.hostel
        )
        self.room.save()

    @tag('book-form-now')
    def test_book_form(self):
        url = reverse('book:now', kwargs={'slug': str(self.hostel.slug), 'room_number': str(self.room.room_number)})
        # the phone number should be in the correct format
        data_1 = {
            'name': 'tester',
            'phone_number': '3534536454'
        }
        response = self.client.post(url, data_1)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book/now.html')
        self.assertContains(response, "Please start with &#39;07&#39;")

        # phone number should be only digits
        data_1['phone_number'] = 'iii09janei'
        response = self.client.post(url, data_1)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book/now.html')
        self.assertContains(response, 'A phone number consists of only digits')
