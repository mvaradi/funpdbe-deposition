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


class LoginViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.response = self.client.get(reverse("login"))

    def test_if_login_has_correct_templates(self):
        self.assertEqual(self.response.template_name, ['login.html'])

    def test_if_login_is_rendered(self):
        self.assertTrue(self.response.is_rendered)

    def test_if_existing_user_can_log_in(self):
        user = User.objects.create_user('test', 'test@test.test', 'test')
        self.assertTrue(self.client.login(username='test', password='test'))
        user.delete()

    def test_if_not_existing_user_cannot_log_in(self):
        self.assertFalse(self.client.login(username="foo", password="bar"))

    def test_if_correct_login_redirects(self):
        user = User.objects.create_user('test', 'test@test.test', 'test')
        login = self.client.post(reverse("login"), {"username": "test", "password": "test"})
        self.assertEqual(login.status_code, 302)
        user.delete()

    def test_if_incorrect_login_reloads_login(self):
        login = self.client.post(reverse("login"), {"username": "foo", "password": "bar"})
        self.assertEqual(login.status_code, 200)


class RegisterViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.response = self.client.get(reverse("register"))

    def test_if_reloads_if_bad_data_is_posted(self):
        register = self.client.post(reverse("register"), {"foo":"bar"})
        self.assertEqual(register.status_code, 200)

    def test_if_redirects_if_valid_data_is_posted(self):
        register = self.client.post(reverse("register"), {
            "username": "test",
            "first_name": "test",
            "last_name": "test",
            "email": "test@test.hu",
            "password1": "asdasd42",
            "password2": "asdasd42"
        })
        self.assertEqual(register.status_code, 302)


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
