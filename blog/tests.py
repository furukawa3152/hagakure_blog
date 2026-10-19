from allauth.socialaccount.models import SocialLogin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.test import override_settings, RequestFactory, TestCase
from wagtail.models import Page, Site
from unittest import mock
import importlib
import uuid
from zoneinfo import ZoneInfo

from blog.forms import BlogPageForm
from blog.models import BlogIndexPage, BlogPage, Comment, Like
from home.models import HomePage


class BlogPageFormTests(TestCase):
    """BlogPageForm.clean_tags の制約を検証"""
    class TagOnlyForm(BlogPageForm):
        class Meta:
            model = BlogPage
            fields = ("tags",)

    def setUp(self):
        self.index = self._create_index_page()

    def _create_index_page(self):
        root = Page.get_first_root_node()
        home = HomePage(title="Home", slug=f"home-{uuid.uuid4().hex[:8]}")
        root.add_child(instance=home)
        home.save_revision().publish()

        index = BlogIndexPage(title="Blog", slug=f"blog-{uuid.uuid4().hex[:8]}")
        home.add_child(instance=index)
        index.save_revision().publish()
        return index

    def test_tag_validation_rejects_more_than_four(self):
        form = self.TagOnlyForm(
            data={"tags": "a,b,c,d,e"},
            parent_page=self.index,
            instance=BlogPage(title="t", slug="t", body=[]),
        )

        self.assertFalse(form.is_valid())
        self.assertIn("tags", form.errors)

    def test_tag_validation_rejects_long_label(self):
        # "テストテストテ" => 6 全角 chars -> 12 counted chars (> 10)
        form = self.TagOnlyForm(
            data={"tags": "テストテストテ"},
            parent_page=self.index,
            instance=BlogPage(title="t", slug="t2", body=[]),
        )

        self.assertFalse(form.is_valid())
        self.assertIn("tags", form.errors)


class BlogPageModelTests(TestCase):
    """BlogPage のユーティリティ（slug固定・検索・いいね重複防止）を検証"""
    def setUp(self):
        self._signal_patchers = [
            mock.patch("blog.signals.review_blog_content", return_value="", create=True),
            mock.patch("blog.signals.log_to_sheet", return_value=True, create=True),
            mock.patch("blog.signals.send_slack_notification", return_value=None, create=True),
        ]
        for patcher in self._signal_patchers:
            patcher.start()
            self.addCleanup(patcher.stop)

        root = Page.get_first_root_node()
        self.home = HomePage(title="Home", slug=f"home-{uuid.uuid4().hex[:8]}")
        root.add_child(instance=self.home)
        self.home.save_revision().publish()

        self.index = BlogIndexPage(title="Blog", slug=f"blog-{uuid.uuid4().hex[:8]}")
        self.home.add_child(instance=self.index)
        self.index.save_revision().publish()

    def _create_live_blog_page(self, title="Like me"):
        page = BlogPage(title=title, slug=f"page-{uuid.uuid4().hex[:8]}", body=[])
        self.index.add_child(instance=page)
        page.save_revision().publish()
        return page

    def test_slug_locked_to_id_on_create(self):
        page = BlogPage(title="Test page", slug="temp", body=[])
        self.index.add_child(instance=page)
        page.save_revision().publish()
        page.refresh_from_db()

        self.assertEqual(page.slug, str(page.id))
        self.assertTrue(page.url_path.rstrip("/").endswith(str(page.id)))

    def test_index_context_filters_by_tag_and_keyword(self):
        tagged = BlogPage(title="Tagged", slug="tagged", body=[])
        self.index.add_child(instance=tagged)
        tagged.tags.add("python")
        tagged.save_revision().publish()

        other = BlogPage(title="Other", slug="other", body=[])
        self.index.add_child(instance=other)
        other.tags.add("django")
        other.save_revision().publish()

        request = RequestFactory().get("/blog/", {"tag": "python", "q": "py"})
        context = self.index.get_context(request)

        blogpages = list(context["blogpages"].object_list)
        self.assertIn(tagged, blogpages)
        self.assertNotIn(other, blogpages)

    def test_index_context_counts_comments_without_tag_duplicates(self):
        page = BlogPage(title="Commented", slug="commented", body=[])
        self.index.add_child(instance=page)
        page.tags.add("python", "pytest")
        page.save_revision().publish()
        user = get_user_model().objects.create_user(username="reader", password="x")
        Comment.objects.create(blogpage=page, user=user, body="one")
        Comment.objects.create(blogpage=page, user=user, body="two")

        request = RequestFactory().get("/blog/", {"tag": "python", "q": "py"})
        context = self.index.get_context(request)

        listed = list(context["blogpages"].object_list)
        self.assertEqual([item.pk for item in listed], [page.pk])
        self.assertEqual(listed[0].comment_count, 2)

    def test_like_unique_per_ip(self):
        page = self._create_live_blog_page()

        Like.objects.create(blogpage=page, ip_address="127.0.0.1", count=1)

        with self.assertRaises(IntegrityError):
            Like.objects.create(blogpage=page, ip_address="127.0.0.1", count=1)

    def test_like_api_accepts_batched_amount(self):
        page = self._create_live_blog_page()

        response = self.client.post(
            f"/like/{page.id}/",
            data='{"amount": 5}',
            content_type="application/json",
            REMOTE_ADDR="127.0.0.9",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["likes"], 5)
        self.assertEqual(
            Like.objects.get(blogpage=page, ip_address="127.0.0.9").count,
            5,
        )

    def test_like_api_caps_batched_amount_and_total_count(self):
        page = self._create_live_blog_page()
        Like.objects.create(blogpage=page, ip_address="127.0.0.9", count=990)

        response = self.client.post(
            f"/like/{page.id}/",
            data='{"amount": 200}',
            content_type="application/json",
            REMOTE_ADDR="127.0.0.9",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["likes"], 999)
        self.assertEqual(
            Like.objects.get(blogpage=page, ip_address="127.0.0.9").count,
            999,
        )


class CommentTests(TestCase):
    def setUp(self):
        self._signal_patchers = [
            mock.patch("blog.signals.generate_hagakure_summary", return_value="要約でござる"),
            mock.patch("blog.signals.review_blog_content", return_value=""),
            mock.patch("blog.signals.log_to_sheet", return_value=True),
            mock.patch("blog.signals.send_slack_notification", return_value=None),
        ]
        for patcher in self._signal_patchers:
            patcher.start()
            self.addCleanup(patcher.stop)

        root = Page.get_first_root_node()
        home = HomePage(title="Home", slug=f"home-{uuid.uuid4().hex[:8]}")
        root.add_child(instance=home)
        home.save_revision().publish()
        site = Site.objects.filter(is_default_site=True).first()
        if site:
            site.hostname = "testserver"
            site.port = 80
            site.root_page = home
            site.save()
        else:
            Site.objects.create(
                hostname="testserver",
                port=80,
                root_page=home,
                is_default_site=True,
            )

        index = BlogIndexPage(title="Blog", slug=f"blog-{uuid.uuid4().hex[:8]}")
        home.add_child(instance=index)
        index.save_revision().publish()

        self.page = BlogPage(title="Comments", slug="comments", body=[])
        index.add_child(instance=self.page)
        self.page.save_revision().publish()

        self.user = get_user_model().objects.create_user(
            username="commenter",
            password="password",
        )

    def test_login_is_required_to_post(self):
        response = self.client.post(
            f"/comment/{self.page.id}/",
            {"body": "コメント"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Comment.objects.exists())

    def test_logged_in_user_can_post(self):
        self.client.force_login(self.user)

        response = self.client.post(
            f"/comment/{self.page.id}/",
            {"body": "  分かりやすい記事でした  "},
        )

        self.assertRedirects(
            response,
            f"{self.page.url}#comments",
            fetch_redirect_response=False,
        )
        comment = Comment.objects.get()
        self.assertEqual(comment.user, self.user)
        self.assertEqual(comment.body, "分かりやすい記事でした")

    def test_comment_accepts_emoji(self):
        self.client.force_login(self.user)

        response = self.client.post(
            f"/comment/{self.page.id}/",
            {"body": "うれしい😀"},
        )

        self.assertRedirects(
            response,
            f"{self.page.url}#comments",
            fetch_redirect_response=False,
        )
        self.assertEqual(Comment.objects.get().body, "うれしい😀")

    def test_comment_accepts_2000_characters(self):
        self.client.force_login(self.user)

        response = self.client.post(
            f"/comment/{self.page.id}/",
            {"body": "あ" * 2000},
        )

        self.assertRedirects(
            response,
            f"{self.page.url}#comments",
            fetch_redirect_response=False,
        )
        self.assertEqual(Comment.objects.get().body, "あ" * 2000)

    def test_comment_rejects_more_than_2000_characters(self):
        self.client.force_login(self.user)

        response = self.client.post(
            f"/comment/{self.page.id}/",
            {"body": "あ" * 2001},
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(Comment.objects.exists())

    @override_settings(
        STORAGES={
            "default": {
                "BACKEND": "django.core.files.storage.FileSystemStorage",
            },
            "staticfiles": {
                "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
            },
        }
    )
    def test_public_page_shows_expand_button_and_escapes_comments(self):
        for number in range(4):
            Comment.objects.create(
                blogpage=self.page,
                user=self.user,
                body=f"<script>{number}</script>",
            )

        response = self.client.get(self.page.url)
        html = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn("data-comment-more", html)
        self.assertIn("comment-card--extra", html)
        self.assertNotIn("<script>0</script>", html)
        self.assertIn("&lt;script&gt;0&lt;/script&gt;", html)
        posted_at = Comment.objects.latest("created_at").created_at.astimezone(
            ZoneInfo("Asia/Tokyo")
        )
        self.assertIn(
            f"{posted_at.year}/{posted_at.month}/{posted_at.day} {posted_at:%H:%M}",
            html,
        )


class DraftReviewApiTests(TestCase):
    """管理画面のAI下書きレビューAPIを検証"""
    def setUp(self):
        root = Page.get_first_root_node()
        self.home = HomePage(title="Home", slug=f"home-{uuid.uuid4().hex[:8]}")
        root.add_child(instance=self.home)
        self.home.save_revision().publish()

        self.index = BlogIndexPage(title="Blog", slug=f"blog-{uuid.uuid4().hex[:8]}")
        self.home.add_child(instance=self.index)
        self.index.save_revision().publish()

        admin_perm = Permission.objects.get(codename="access_admin")

        self.user = get_user_model().objects.create_user(
            username="editor", email="editor@example.com", password="x", is_staff=True, is_superuser=True
        )
        self.user.user_permissions.add(admin_perm)
        self.user.save()

    def _create_draft_page(self):
        page = BlogPage(
            title="Draft",
            slug=f"draft-{uuid.uuid4().hex[:8]}",
            body=[("rich_text", "<p>hello</p>")],
        )
        self.index.add_child(instance=page)
        page.save_revision()  # keep as draft
        return page

    @mock.patch("blog.views.review_blog_content", return_value="拙者のレビューでござる")
    def test_returns_review_for_editable_page(self, mock_review):
        page = self._create_draft_page()
        self.client.force_login(self.user)

        response = self.client.post(f"/admin/api/draft-review/{page.id}/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["review"], "拙者のレビューでござる")
        mock_review.assert_called_once()

    def test_forbids_user_without_edit_permission(self):
        page = self._create_draft_page()
        viewer = get_user_model().objects.create_user(
            username="viewer", password="x", is_staff=True
        )
        viewer.user_permissions.add(Permission.objects.get(codename="access_admin"))
        viewer.save()
        self.client.force_login(viewer)

        response = self.client.post(f"/admin/api/draft-review/{page.id}/")

        self.assertEqual(response.status_code, 403)


class AuthAdapterTests(TestCase):
    """Google OAuthアダプタのホワイトリスト/権限付与を検証"""
    def setUp(self):
        self.rf = RequestFactory()
        self.user_model = get_user_model()

        # avoid hitting Google Sheets during import
        patcher = mock.patch(
            "mysite.settings.google_email_whitelist.read_account_sheet.read_acount_list",
            return_value=[],
        )
        self.addCleanup(patcher.stop)
        patcher.start()

        # reload adapters after patching
        self.adapters = importlib.reload(importlib.import_module("adapters"))
        self.adapter_allowed = self.adapters.allowed

    def tearDown(self):
        self.adapter_allowed[:] = []

    def test_pre_social_login_blocks_unlisted_email(self):
        self.adapter_allowed[:] = ["allowed@example.com"]
        adapter = self.adapters.CustomSocialAccountAdapter()

        user = self.user_model(email="blocked@example.com")
        sociallogin = SocialLogin()
        sociallogin.user = user

        with self.assertRaises(PermissionDenied):
            adapter.pre_social_login(self.rf.get("/"), sociallogin)

    def test_save_user_assigns_staff_and_group(self):
        self.adapter_allowed[:] = ["allowed@example.com"]
        adapter = self.adapters.CustomSocialAccountAdapter()

        user = self.user_model.objects.create(email="allowed@example.com", username="allowed")
        sociallogin = SocialLogin()
        sociallogin.user = user

        with mock.patch.object(self.adapters.DefaultSocialAccountAdapter, "save_user", return_value=user):
            saved_user = adapter.save_user(self.rf.get("/"), sociallogin)
        editors_group = Group.objects.get(name="Editors")

        self.assertTrue(saved_user.is_staff)
        self.assertIn(editors_group, saved_user.groups.all())
