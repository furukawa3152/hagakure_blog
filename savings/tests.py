from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from .forms import SavingEntryForm
from .models import RewardSpend, SavingEntry


class SavingsAppTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username="saver", password="pass")
        self.other = user_model.objects.create_user(username="other", password="pass")

    def test_records_are_scoped_to_logged_in_user(self):
        SavingEntry.objects.create(
            user=self.user,
            title="ジュース",
            category=SavingEntry.CATEGORY_DRINK,
            amount=180,
        )
        SavingEntry.objects.create(
            user=self.other,
            title="他人だけの記録",
            category=SavingEntry.CATEGORY_BOOK,
            amount=1200,
        )
        RewardSpend.objects.create(user=self.user, title="温泉", amount=500, satisfaction=5)

        self.client.force_login(self.user)
        response = self.client.get("/savings/")

        self.assertContains(response, "ジュース")
        self.assertContains(response, "-320円")
        self.assertNotContains(response, "他人だけの記録")

    def test_create_saving_attaches_user_and_roast(self):
        self.client.force_login(self.user)

        response = self.client.post(
            "/savings/save/",
            {
                "title": "ジュース",
                "category": SavingEntry.CATEGORY_DRINK,
                "amount": 180,
                "avoided_on": "2026-04-30",
                "note": "",
            },
        )

        self.assertRedirects(response, "/savings/")
        saving = SavingEntry.objects.get(user=self.user)
        self.assertEqual(saving.amount, 180)
        self.assertTrue(saving.roast_text)

    def test_saving_amount_rejects_full_width_digits(self):
        form = SavingEntryForm(
            data={
                "title": "ジュース",
                "category": SavingEntry.CATEGORY_DRINK,
                "amount": "１８０",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("amount", form.errors)

    def test_saving_title_is_optional(self):
        form = SavingEntryForm(
            data={
                "title": "",
                "category": SavingEntry.CATEGORY_DRINK,
                "amount": "180",
            }
        )

        self.assertTrue(form.is_valid(), form.errors)

    @override_settings(DEBUG=True)
    def test_login_page_uses_dev_login_without_google_oauth_settings(self):
        response = self.client.get("/accounts/login/?next=/savings/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "開発用ログイン")

    @override_settings(DEBUG=True)
    def test_dev_login_redirects_to_savings(self):
        response = self.client.post("/savings/dev-login/", {"next": "/savings/"})

        self.assertRedirects(response, "/savings/")
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_cannot_delete_another_users_record(self):
        saving = SavingEntry.objects.create(
            user=self.other,
            title="他人の記録",
            category=SavingEntry.CATEGORY_OTHER,
            amount=999,
        )
        self.client.force_login(self.user)

        response = self.client.post(f"/savings/save/{saving.pk}/delete/")

        self.assertEqual(response.status_code, 404)
        self.assertTrue(SavingEntry.objects.filter(pk=saving.pk).exists())
