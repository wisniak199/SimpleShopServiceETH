from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from shop.models import Session
from django.conf import settings


class AccountTests(APITestCase):
    def setUp(self):
        self.etherum_address = '0x55a0b7892bA87c015f88808e62d5658614Bec424'
        self.session_id = '0x3129042299270b945ba819991b82d07285772951e5e99060e044e1eb09cf5f64'
        self.receipt_0 = '0x8efd4a3846654ab554b9efca8a3d0d631528a9d4f6236d014fe97cc794d7e6f56e96df449972a3b514441b331f0c5f6f2eea3aa9078c3c423c7466a0d85eedc001'
        self.receipt_1 = '0x892ab911a4dbec3838d285351d8927e2c471b1ea7302335980694a1f4804c38f422fd66995cc2bb9d62fa3d479fa160728ee1d27e5d955ef5ed9047af3a7368300'
        self.value = 1

    def test_start_session(self):
        receipt = ''
        url = reverse('start-session')
        data = {
            'session_id': self.session_id,
            'receipt': self.receipt_0,
            'etherum_address': self.etherum_address,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Session.objects.all().count(), 1)
        session = Session.objects.all().first()
        self.assertEqual(session.receipt_value, 0)

    def test_buy_content(self):
        start_session_url = reverse('start-session')
        buy_content_url = reverse('buy-content')
        start_session_data = {
            'session_id': self.session_id,
            'receipt': self.receipt_0,
            'etherum_address': self.etherum_address,
        }
        buy_content_data = {
            'receipt': self.receipt_1
        }
        self.client.post(start_session_url, start_session_data)
        response = self.client.post(buy_content_url, buy_content_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Session.objects.all().count(), 1)
        session = Session.objects.all().first()
        self.assertEqual(session.receipt_value, settings.CONTENT_PRICE)
