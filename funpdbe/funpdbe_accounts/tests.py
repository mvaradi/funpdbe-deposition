from django.test import TestCase, Client
from django.contrib.auth.models import User


class UrlTests(TestCase):

    def test_if_login_url_is_valid(self):
        c = Client()
        response = c.get('/funpdbe_accounts/login')
        self.assertEqual(response.status_code, 200)

    def test_if_logout_url_is_valid(self):
        c = Client()
        response = c.get('/funpdbe_accounts/logout')
        self.assertEqual(response.status_code, 302)

    def test_if_register_url_is_valid(self):
        c = Client()
        response = c.get('/funpdbe_accounts/register')
        self.assertEqual(response.status_code, 200)

    def test_if_home_url_is_valid(self):
        c = Client()
        response = c.get('/funpdbe_accounts/home')
        self.assertEqual(response.status_code, 302)

    def test_if_logout_redirects_to_home(self):
        c = Client()
        response = c.get('/funpdbe_accounts/logout', follow=True)
        self.assertEqual(response.redirect_chain[0][0], 'home')


class ViewTests(TestCase):

    def test_if_home_redirects_if_not_logged_in(self):
        c = Client()
        response = c.get('/funpdbe_accounts/home')
        self.assertEqual(response.status_code, 302)

    def test_if_home_renders_when_logged_in(self):
        user = User.objects.create_user('test', 'test@test.test', 'test')
        c = Client()
        c.login(username='test', password='test')
        response = c.get('/funpdbe_accounts/home')
        self.assertEqual(response.status_code, 200)

