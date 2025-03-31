from django.test import TestCase
from django.db.utils import IntegrityError
from django.utils.timezone import now
from accounts.models import CustomUser
from news_app.models import Article
from datetime import date


class ArticleModelTest(TestCase):
    def setUp(self):
        # テストユーザーを作成
        self.user = CustomUser.objects.create_user(username='testuser', password='testpass')

    # 正常系：Articleが保存・取得できる
    def test_article_creation(self):
        article = Article.objects.create(
            user=self.user,
            article_title="Test Title",
            article_url="https://example.com/article",
            article_img_url="https://example.com/image.jpg",
            memo="This is a memo.",
            published_at=date(2025, 3, 30)
        )

        # 保存された内容が正しいか確認
        self.assertEqual(article.article_title, "Test Title")
        self.assertEqual(article.memo, "This is a memo.")
        self.assertEqual(article.user.username, "testuser")
        self.assertEqual(article.article_url, "https://example.com/article")
        self.assertEqual(article.article_img_url, "https://example.com/image.jpg")
        self.assertEqual(article.published_at, date(2025, 3, 30))
        self.assertIsNotNone(article.created_at)
        self.assertIsNotNone(article.updated_at)

    # __str__ のテスト：記事タイトルが返ることを確認
    def test_str_returns_title(self):
        article = Article.objects.create(
            user=self.user,
            article_title="Readable Title",
            article_url="https://example.com/article1"
        )
        self.assertEqual(str(article), "Readable Title")

    # 異常系1：ユニーク制約違反（同じuser＋URL）
    def test_duplicate_article_url_for_same_user_raises_integrity_error(self):
        Article.objects.create(
            user=self.user,
            article_url="https://example.com/article3"
        )

        # 同じユーザー & URL の記事は保存できない。例外が発生すればOK。
        with self.assertRaises(IntegrityError):
            Article.objects.create(
                user=self.user,
                article_url="https://example.com/article3"
            )

    # OKケース：同じURLでもuserが違えば保存できる
    def test_same_url_different_user_is_allowed(self):
        other_user = CustomUser.objects.create_user(username='otheruser', password='testpass')

        Article.objects.create(
            user=self.user,
            article_url="https://example.com/article4"
        )

        # 違うユーザーなら同じURLでも保存できる。例外が発生しなければOK。
        try:
            Article.objects.create(
                user=other_user,
                article_url="https://example.com/article4"
            )
        except IntegrityError:
            self.fail("別のユーザーなのに、ユニーク制約エラー（IntegrityError）が予期せず発生しました。")
