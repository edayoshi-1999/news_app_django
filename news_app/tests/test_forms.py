from django.test import TestCase
from accounts.models import CustomUser
from news_app.models import Article
from news_app.forms import AddFavoriteForm
from datetime import date

class AddFavoriteFormTest(TestCase):
    # setUp() メソッドは各テストの直前に毎回呼ばれる
    def setUp(self):
        # ユーザーと初期データの作成
        self.user = CustomUser.objects.create_user(username='user1', password='testpass')
        self.other_user = CustomUser.objects.create_user(username='user2', password='testpass')

        self.article = Article.objects.create(
            user=self.user,
            article_title="重複チェックテスト",
            article_url="https://example.com/article",
            published_at=date(2025, 3, 30)
        )

    # 正常系：重複がなければフォームは有効
    def test_valid_form(self):
        form_data = {
            'article_title': '新しい記事',
            'article_url': 'https://example.com/new-article',
            'article_img_url': '',
            'published_at': '2025-03-30',
            'memo': 'メモ'
        }
        form = AddFavoriteForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid())

    # 異常系：同じURLを同じユーザーが登録しようとしたらエラー
    def test_duplicate_url_same_user_invalid(self):
        form_data = {
            'article_title': 'ダブり',
            'article_url': 'https://example.com/article',  # 重複！
            'published_at': '2025-03-30',
            'memo': 'test'
        }
        form = AddFavoriteForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('article_url', form.errors)
        self.assertEqual(form.errors['article_url'][0], "この記事はすでに登録されています。")

    # 正常系：他のユーザーが同じURLなら登録できる
    def test_same_url_different_user_valid(self):
        form_data = {
            'article_title': '他ユーザー',
            'article_url': 'https://example.com/article',  # 同じURLだけど別ユーザー
            'published_at': '2025-03-30',
            'memo': '別の人'
        }
        form = AddFavoriteForm(data=form_data, user=self.other_user)
        self.assertTrue(form.is_valid())

    # 正常系：編集中なら自分のURLはOK（pkで除外される）
    def test_update_own_article_valid(self):
        form_data = {
            'article_title': '更新テスト',
            'article_url': 'https://example.com/article',  # 自分のURL
            'published_at': '2025-03-30',
            'memo': '更新中'
        }
        form = AddFavoriteForm(data=form_data, instance=self.article, user=self.user)
        self.assertTrue(form.is_valid())
