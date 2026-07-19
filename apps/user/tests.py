from django.contrib.auth import get_user_model
from rest_framework import status, test

User = get_user_model()


class TestUserAuth(test.APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="test@example.com",
            password="StrongPass123",
            first_name="John",
            phone_number="9876543210",
        )

    # Register

    def test_register_success(self):
        data = {
            "email": "new@example.com",
            "password": "StrongPass123",
            "first_name": "Jane",
            "phone_number": "9876543211",
        }

        res = self.client.post("/api/auth/register/", data)

        # response
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.cookies)

        # database
        user = User.objects.get(email="new@example.com")
        self.assertEqual(user.first_name, "Jane")
        self.assertEqual(user.phone_number, "9876543211")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.check_password("StrongPass123"))

    def test_register_email_normalized(self):
        self.client.post(
            "/api/auth/register/",
            {
                "email": "UPPER@EXAMPLE.COM",
                "password": "123",
                "first_name": "A",
                "phone_number": "9876543212",
            },
        )

        self.assertTrue(User.objects.filter(email="upper@example.com").exists())

    def test_register_duplicate_email(self):
        res = self.client.post(
            "/api/auth/register/",
            {
                "email": self.user.email,
                "password": "123",
                "first_name": "A",
                "phone_number": "9876543213",
            },
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_invalid_phone(self):
        res = self.client.post(
            "/api/auth/register/",
            {
                "email": "x@test.com",
                "password": "123",
                "first_name": "A",
                "phone_number": "0000000000",
            },
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # Login

    def test_login_success(self):
        res = self.client.post(
            "/api/auth/login/",
            {
                "email": self.user.email,
                "password": "StrongPass123",
            },
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.cookies)

    def test_login_wrong_password(self):
        res = self.client.post(
            "/api/auth/login/",
            {
                "email": self.user.email,
                "password": "wrong",
            },
        )

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_email_case_insensitive(self):
        res = self.client.post(
            "/api/auth/login/",
            {
                "email": "TEST@EXAMPLE.COM",
                "password": "StrongPass123",
            },
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    # Refresh

    def test_refresh_success(self):
        login = self.client.post(
            "/api/auth/login/",
            {
                "email": self.user.email,
                "password": "StrongPass123",
            },
        )

        self.client.cookies["refresh"] = login.cookies["refresh"].value

        res = self.client.post("/api/auth/token/refresh/")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("access", res.data)

    def test_refresh_missing_cookie(self):
        res = self.client.post("/api/auth/token/refresh/")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # Helpers

    def authenticate(self):
        login = self.client.post(
            "/api/auth/login/",
            {
                "email": self.user.email,
                "password": "StrongPass123",
            },
        )
        self.access = login.data["access"]
        self.refresh = login.cookies["refresh"].value
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")
        self.client.cookies["refresh"] = self.refresh

    # Token rotation

    def test_refresh_rotates_token(self):
        self.authenticate()

        res = self.client.post("/api/auth/token/refresh/")

        new_refresh = res.cookies["refresh"].value

        self.assertNotEqual(self.refresh, new_refresh)

    def test_old_refresh_invalid_after_rotation(self):
        self.authenticate()

        res = self.client.post("/api/auth/token/refresh/")
        new_refresh = res.cookies["refresh"].value

        # old should fail
        self.client.cookies["refresh"] = self.refresh
        res = self.client.post("/api/auth/token/refresh/")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

        # new should work
        self.client.cookies["refresh"] = new_refresh
        res = self.client.post("/api/auth/token/refresh/")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    # Logout

    def test_logout_clears_cookie(self):
        self.authenticate()

        res = self.client.post("/api/auth/logout/")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.cookies["refresh"].value, "")

    def test_logout_blacklists_refresh(self):
        self.authenticate()

        self.client.post("/api/auth/logout/")

        self.client.cookies["refresh"] = self.refresh
        res = self.client.post("/api/auth/token/refresh/")

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    # User endpoints

    def test_get_user(self):
        self.authenticate()

        res = self.client.get("/api/user/")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["email"], self.user.email)
        self.assertEqual(res.data["first_name"], self.user.first_name)

    def test_update_user(self):
        self.authenticate()

        res = self.client.patch("/api/user/", {"first_name": "Updated"})

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")

    def test_delete_user_soft_delete(self):
        self.authenticate()

        res = self.client.delete("/api/user/")

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)

        # cookie cleared
        self.assertEqual(res.cookies["refresh"].value, "")

    def test_user_requires_auth(self):
        res = self.client.get("/api/user/")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
