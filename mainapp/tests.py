from decimal import Decimal
from unittest import mock
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import Category, Notebook, CartProduct, Cart, Customer
from .views import recalc_cart, AddToCartView, BaseView

User = get_user_model()


class ShopTestCases(TestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(username="Alik", password="0000")
        self.category = Category.objects.create(name='Ноутбуки', slug='notebooks')
        image = SimpleUploadedFile("Asus's laptop.png", content=b'', content_type="image/png")
        self.notebook = Notebook.objects.create(
            category=self.category,
            title="Test Notebook",
            slug="test-slug",
            image=image,
            price=Decimal('560000.00'),
            diagonal="15",
            display_type="IPS",
            proccesor_freq="3.4Ghz",
            ram="16Gb",
            video="Nvidia RTX2060",
            time_without_charge="9 часов"
        )

        self.customer = Customer.objects.create(user=self.user, phone="11111111122", address="adres")
        self.cart = Cart.objects.create(owner=self.customer)
        self.cart_product = CartProduct.create(
            user=self.customer,
            cart=self.cart,
            content_object=self.notebook
        )

        def test_add_to_cart(self):
            self.cart.products.add(self.cart_product)
            recalc_cart(self.cart)
            self.assertIn(self.cart_product, self.cart.products.all())
            self.assertEqual(self.cart.products.count(), 1)
            self.assertEqual(self.cart.final_price, Decimal('560000.00'))

        def test_response_from_add_to_cart_view(self):
            factory = RequestFactory()
            request = factory.get('')
            request.user = self.user
            response = AddToCartView.as_view()(request, ct_model="notebook", slug="test-slug")
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, '/cart/')

