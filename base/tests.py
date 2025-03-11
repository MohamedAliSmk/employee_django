from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

class CustomUserTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.username = "staffuser"
        self.email = "staffuser@example.com"
        self.password = "secure_password"
        self.user = self.user_model.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password
        )
        self.user.is_staff = True  # Allow admin access
        self.user.save()

    def test_user_creation(self):
        """
        Test if the user is created successfully with a hashed password.
        """
        self.assertIsNotNone(self.user)
        self.assertEqual(self.user.username, self.username)
        self.assertEqual(self.user.email, self.email)
        # Check if the password is hashed
        self.assertNotEqual(self.user.password, self.password)
        self.assertTrue(self.user.check_password(self.password))

    def test_login(self):
        """
        Test if the user can log in with the correct credentials.
        """
        user = authenticate(username=self.username, password=self.password)
        self.assertIsNotNone(user)
        self.assertEqual(user, self.user)

    def test_login_with_invalid_credentials(self):
        """
        Test login with invalid credentials.
        """
        user = authenticate(username=self.username, password="wrong_password")
        self.assertIsNone(user)

    def test_superuser_creation(self):
        """
        Test creating a superuser.
        """
        admin = self.user_model.objects.create_superuser(
            username="adminuser",
            email="adminuser@example.com",
            password="admin_password"
        )
        self.assertIsNotNone(admin)
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.check_password("admin_password"))

    def test_is_staff_flag(self):
        """
        Test if the is_staff flag is working correctly.
        """
        self.assertTrue(self.user.is_staff)

    def test_admin_login(self):
        """
        Test if a staff user can log in to the admin portal.
        """
        user = authenticate(username=self.username, password=self.password)
        self.assertIsNotNone(user)
        self.assertTrue(user.is_staff)