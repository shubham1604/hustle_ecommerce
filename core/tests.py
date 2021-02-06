from django.test import TestCase
from django.urls import reverse
from .forms.signup import SignUpForm
from .models import Product, Categories
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings


class RegisterTests(TestCase):

    def setUp(self):
        self.response = self.client.get('/register/')
        # self.client =

    def test_view_success_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_view_accessible_by_name(self):
        self.response = self.client.get(reverse('register'))
        self.assertEquals(self.response.status_code, 200)

    def test_view_uses_correct_template(self):
        self.assertEquals(self.response.status_code, 200)
        self.assertTemplateUsed(self.response, "registration/signup.html")

    def test_view_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form,SignUpForm)

    def test_csrf_token(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

class HomeTests(TestCase):

    @classmethod
    def setUpTestData(cls):

        category  = Categories(**{'category_name':f"cat_{0}"})
        category.save()
        product = Product(**{'product_title':f"name_{0}",
        'price':1,
        'descr':'test descr',
        'product_category':category,
        'image':SimpleUploadedFile(name='black-kacket.jpg', content=b'', content_type='image/jpeg')
        })
        product.save()

    def setUp(self):
        self.response = self.client.get('')

    def test_view_success_status_code(self):
        self.assertEquals(self.response.status_code,200)

    def test_view_accessible_by_name(self):
        response = self.client.get(reverse('home'))
        self.assertEquals(response.status_code, 200)

    def test_view_uses_correct_template(self):
        self.assertTemplateUsed(self.response, "home-page.html")

    def test_view_contains_product_detail_view_link(self):
        product = Product.objects.get(pk = 1)
        product_detail_view_link = reverse('product', kwargs={'pk':product.pk})
        self.assertContains(self.response, 'href = "{0}"'.format(product_detail_view_link))

    
