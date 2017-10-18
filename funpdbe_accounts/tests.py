from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse


class UrlTests(TestCase):

    def setUp(self):
        self.client = Client()

    # Tests specific to register url
    def test_if_register_url_is_valid(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)

    # Tests specific to login url
    def test_if_login_url_is_valid(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    # Tests specific to logout url
    def test_if_logout_url_is_valid(self):
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)

    def test_if_logout_redirects_to_home(self):
        response = self.client.get(reverse("logout"), follow=True)
        self.assertEqual(response.redirect_chain[0][0], 'home')

    # Tests specific to home url
    def test_if_home_url_is_valid(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 302)


class ViewTests(TestCase):

    def setUp(self):
        self.client = Client()

    # Tests specific to home view
    def test_if_home_redirects_if_not_logged_in(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 302)

    def test_if_home_renders_when_logged_in(self):
        user = User.objects.create_user('test', 'test@test.test', 'test')
        self.client.login(username='test', password='test')
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

