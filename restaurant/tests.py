from datetime import datetime, timezone
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.staticfiles import finders
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import Booking, Menu


BOOKING = {"name": "Taylor", "no_of_guests": 4, "booking_date": "2027-05-10T18:30:00Z"}
MENU = {"title": "Greek salad", "price": "12.50", "inventory": 20}
PASSWORD = "Ridge!Amber-73-Copper"


class RestaurantModelTests(TestCase):
    def test_menu_round_trip(self):
        item = Menu.objects.create(**MENU)
        item.refresh_from_db()
        self.assertEqual(str(item), "Greek salad")
        self.assertEqual(item.price, Decimal("12.50"))
        self.assertEqual(item.inventory, 20)

    def test_booking_round_trip(self):
        booking = Booking.objects.create(**BOOKING)
        booking.refresh_from_db()
        self.assertEqual(str(booking), "Taylor")
        self.assertEqual(booking.no_of_guests, 4)
        self.assertEqual(booking.booking_date, datetime(2027, 5, 10, 18, 30, tzinfo=timezone.utc))

    def test_booking_validates_party_size(self):
        booking = Booking(**{**BOOKING, "no_of_guests": 0})
        with self.assertRaises(ValidationError):
            booking.full_clean()

    def test_homepage_references_existing_css(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Little Lemon")
        self.assertContains(response, "/static/restaurant/site.css")
        self.assertIsNotNone(finders.find("restaurant/site.css"))


class RestaurantAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        users = get_user_model().objects
        cls.staff = users.create_user("staff", password=PASSWORD, is_staff=True)
        cls.guest = users.create_user("guest", password=PASSWORD)
        cls.menu_item = Menu.objects.create(**MENU)

    def authenticate(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_public_menu_list_and_detail(self):
        listing = self.client.get(reverse("menu-list"))
        detail = self.client.get(reverse("menu-detail", args=[self.menu_item.pk]))
        self.assertEqual(listing.status_code, status.HTTP_200_OK)
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(listing.data, [{"id": self.menu_item.pk, **MENU}])
        self.assertEqual(detail.data, listing.data[0])

    def test_menu_missing_item_returns_404(self):
        response = self.client.get(reverse("menu-detail", args=[self.menu_item.pk + 1]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_menu_writes_require_staff_token(self):
        list_url = reverse("menu-list")
        detail_url = reverse("menu-detail", args=[self.menu_item.pk])
        for user, code in [(None, status.HTTP_401_UNAUTHORIZED), (self.guest, status.HTTP_403_FORBIDDEN)]:
            if user:
                self.authenticate(user)
            for method, url in [("post", list_url), ("put", detail_url), ("patch", detail_url), ("delete", detail_url)]:
                with self.subTest(user=user, method=method):
                    response = getattr(self.client, method)(url, MENU, format="json")
                    self.assertEqual(response.status_code, code)

    def test_staff_creates_menu_item(self):
        self.authenticate(self.staff)
        response = self.client.post(reverse("menu-list"), {**MENU, "title": "Bruschetta"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Menu.objects.filter(pk=response.data["id"], title="Bruschetta").exists())

    def test_staff_updates_menu_item(self):
        self.authenticate(self.staff)
        url = reverse("menu-detail", args=[self.menu_item.pk])
        response = self.client.put(url, {**MENU, "price": "14.00"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.patch(url, {"inventory": 18}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.menu_item.refresh_from_db()
        self.assertEqual(self.menu_item.price, Decimal("14.00"))
        self.assertEqual(self.menu_item.inventory, 18)

    def test_staff_deletes_menu_item(self):
        self.authenticate(self.staff)
        response = self.client.delete(reverse("menu-detail", args=[self.menu_item.pk]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Menu.objects.filter(pk=self.menu_item.pk).exists())

    def test_invalid_menu_values_return_400(self):
        self.authenticate(self.staff)
        response = self.client.post(reverse("menu-list"), {**MENU, "price": "-1", "inventory": -2}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(set(response.data), {"price", "inventory"})

    def test_booking_requires_token_for_all_methods(self):
        booking = Booking.objects.create(**BOOKING)
        list_url = reverse("booking-list")
        detail_url = reverse("booking-detail", args=[booking.pk])
        for method, url in [("get", list_url), ("post", list_url), ("get", detail_url),
                            ("put", detail_url), ("patch", detail_url), ("delete", detail_url)]:
            with self.subTest(method=method, url=url):
                self.assertEqual(getattr(self.client, method)(url).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_booking_crud(self):
        self.authenticate(self.guest)
        list_url = reverse("booking-list")
        created = self.client.post(list_url, BOOKING, format="json")
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        booking_id = created.data["id"]
        detail_url = reverse("booking-detail", args=[booking_id])
        listing = self.client.get(list_url)
        detail = self.client.get(detail_url)
        self.assertEqual(listing.status_code, status.HTTP_200_OK)
        self.assertEqual(detail.status_code, status.HTTP_200_OK)
        self.assertEqual(listing.data, [{"id": booking_id, **BOOKING}])
        self.assertEqual(detail.data, listing.data[0])
        put = self.client.put(detail_url, {**BOOKING, "name": "Jordan"}, format="json")
        self.assertEqual(put.status_code, status.HTTP_200_OK)
        patch = self.client.patch(detail_url, {"no_of_guests": 2}, format="json")
        self.assertEqual(patch.status_code, status.HTTP_200_OK)
        self.assertEqual(patch.data["name"], "Jordan")
        self.assertEqual(patch.data["no_of_guests"], 2)
        self.assertEqual(self.client.delete(detail_url).status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.client.get(detail_url).status_code, status.HTTP_404_NOT_FOUND)

    def test_booking_rejects_invalid_guest_count_and_date(self):
        self.authenticate(self.guest)
        response = self.client.post(
            reverse("booking-list"), {**BOOKING, "no_of_guests": 0, "booking_date": "tomorrow"}, format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(set(response.data), {"no_of_guests", "booking_date"})

    def test_registration_and_token_lifecycle(self):
        users_url = reverse("user-list")
        payload = {"username": "reviewer", "email": "reviewer@example.com", "password": PASSWORD}
        registered = self.client.post(users_url, payload, format="json")
        self.assertEqual(registered.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("password", registered.data)
        self.assertEqual(self.client.post(users_url, payload, format="json").status_code, status.HTTP_400_BAD_REQUEST)
        login = self.client.post(
            reverse("login"), {"username": payload["username"], "password": PASSWORD}, format="json",
        )
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {login.data['auth_token']}")
        current = self.client.get(reverse("user-me"))
        self.assertEqual(current.status_code, status.HTTP_200_OK)
        self.assertEqual(current.data["username"], payload["username"])
        self.assertEqual(self.client.get(reverse("booking-list")).status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.post(reverse("logout")).status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.client.get(reverse("user-me")).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_invalid_login_and_invalid_token(self):
        login = self.client.post(reverse("login"), {"username": "guest", "password": "incorrect"}, format="json")
        self.assertEqual(login.status_code, status.HTTP_400_BAD_REQUEST)
        self.client.credentials(HTTP_AUTHORIZATION="Token invalid")
        self.assertEqual(self.client.get(reverse("booking-list")).status_code, status.HTTP_401_UNAUTHORIZED)
