from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth import get_user_model
from news_app.models import Article
from news_app.views import OnlyYouMixin
from django.http import Http404
from unittest.mock import patch
from news_app.views import ForeignNewsView, NikkeiMedView, ZiziMedView

from django.contrib.sessions.middleware import SessionMiddleware


# OnlyYouMixin のテスト
class OnlyYouMixinTests(TestCase):
    # テスト用のデータをセットアップするメソッド
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(username="user", password="pass")
        self.other_user = get_user_model().objects.create_user(username="other", password="pass")
        self.article = Article.objects.create(
            user=self.user,
            article_title="Sample",
            article_url="https://example.com",
            published_at="2025-03-30"
        )

    # 正常系：自分の記事にアクセス → True を返す
    def test_allows_owner_access(self):
        mixin = OnlyYouMixin()
        request = self.client.get("/")
        # ログインユーザーをセット
        request.user = self.user
        mixin.request = request
        mixin.kwargs = {"pk": self.article.pk}
        self.assertTrue(mixin.test_func())

    # 異常系1：他人の記事にアクセス → False を返す
    def test_denies_non_owner_access(self):
        mixin = OnlyYouMixin()
        request = self.client.get("/")
        # 他人のユーザーをセット
        request.user = self.other_user
        mixin.request = request
        mixin.kwargs = {"pk": self.article.pk}
        self.assertFalse(mixin.test_func())

    # 異常系2：記事が存在しない場合 → Http404 を返す
    def test_raises_404_for_invalid_pk(self):
        mixin = OnlyYouMixin()
        request = self.client.get("/")
        request.user = self.user
        mixin.request = request
        mixin.kwargs = {"pk": 9999}  # 存在しない
        
        #Http404を期待する
        with self.assertRaises(Http404): 
            mixin.test_func()

# IndexView のテスト 
class IndexViewTests(TestCase):

    # ログイン不要なトップページが表示され、正しいテンプレートが使われること
    def test_index_view_status_and_template(self):
        response = self.client.get(reverse("news_app:index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")


# ForeignNewsView のテスト
class ForeignNewsViewTests(TestCase):
    # sessionを使うので、RequestFactoryを使ってリクエストを作成する。
    def setUp(self):
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(username='user', password='pass')

    # セッションミドルウェアを使って、リクエストにセッションを追加する。
    # これにより、セッションにデータを保存できるようになる。 
    # request.session["key"] = value のような処理をテストするために必要。
    def add_session_to_request(self, request):
        middleware = SessionMiddleware(get_response=lambda r: None)
        middleware.process_request(request)
        request.session.save()

    #異常系：ログインしていないとき、ログインページへリダイレクトされるか
    def test_requires_login(self):
        response = self.client.get(reverse('news_app:foreign_news'))
        self.assertRedirects(response, f'/accounts/login/?next={reverse("news_app:foreign_news")}')

    # 正常系：ログインしているとき、templateが正しく表示されるか
    def test_foreign_news_view_renders_template(self):
        self.client.login(username="user", password="pass")
        response = self.client.get(reverse("news_app:foreign_news"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "foreign_news.html")  

    #正常系：セッションにデータがなければAPIを呼び、セッションに保存されるか
    @patch("news_app.views.fetch_news_from_api")
    @patch("news_app.views.convert_utc_to_jst", side_effect=lambda dt: "JST:" + dt)
    def test_fetches_from_api_on_first_access(self, mock_convert, mock_fetch):
        mock_fetch.return_value = [
            ["Title", "2025-03-30T12:00:00Z", "Source", "https://example.com", "https://img.jpg"]
        ]

        request = self.factory.get('/foreign_news/')
        request.user = self.user # ログインユーザーをセット。これでログイン済みとみなされる。
        self.add_session_to_request(request) # セッションを追加

        view = ForeignNewsView()
        view.request = request # リクエストをビューにセット

        result = view.get_foreign_news_data()

        self.assertIn("foreign_news_data", request.session) # セッションにデータが保存されているか
        self.assertEqual(result[0][1], "JST:2025-03-30T12:00:00Z")  # convert_utc_to_jst が呼ばれたか
        mock_fetch.assert_called_once() # APIが1回だけ呼ばれたか

    #正常系：セッションにデータがあるときはAPIを呼ばないか
    @patch("news_app.views.fetch_news_from_api")
    def test_uses_session_data_on_second_access(self, mock_fetch):
        request = self.factory.get('/foreign_news/')
        request.user = self.user
        self.add_session_to_request(request)

        # セッションにデータを先に入れておく
        request.session["foreign_news_data"] = [
            ["FromSession", "2025-01-01T00:00:00Z", "source", "url", "img"]
        ]

        view = ForeignNewsView()
        view.request = request
        result = view.get_foreign_news_data()

        self.assertEqual(result[0][0], "FromSession")  # セッションのデータが使われているか
        mock_fetch.assert_not_called() # APIが呼ばれないか

    #正常系： ページネーションが正しく機能しているか
    @patch("news_app.views.fetch_news_from_api")
    @patch("news_app.views.convert_utc_to_jst", side_effect=lambda dt: dt)
    def test_context_contains_page_obj(self, mock_convert, mock_fetch):
        mock_fetch.return_value = [
            ["Title", "2025-03-30T12:00:00Z", "Source", "https://example.com", "https://img.jpg"]
        ] * 15  # 15件返す（10件/ページで2ページ目ができる）

        request = self.factory.get('/foreign_news/?page=2')
        request.user = self.user
        self.add_session_to_request(request)

        view = ForeignNewsView()
        view.request = request
        context = view.get_context_data()

        page_obj = context["page_obj"]
        self.assertTrue(hasattr(page_obj, "object_list")) # page_obj が正しく object_list 属性を持っている（= ページネーションが正常に機能している）か
        self.assertEqual(page_obj.number, 2)  # ページ2が取得できているか

    #正常系：convert_utc_to_jst()がすべての記事に対して呼ばれているか（=ループ内で正しく動いてるか）
    @patch("news_app.views.fetch_news_from_api")
    @patch("news_app.views.convert_utc_to_jst")
    def test_date_conversion_is_applied(self, mock_convert, mock_fetch):
        mock_fetch.return_value = [
            ["Title", "2025-03-30T12:00:00Z", "Source", "https://example.com", "https://img.jpg"],
            ["Title2", "2025-03-30T13:00:00Z", "Source2", "https://example.com", "https://img.jpg"],
            ["Title3", "2025-03-30T14:00:00Z", "Source3", "https://example.com", "https://img.jpg"]
        ]

        mock_convert.side_effect = lambda dt: "JST:" + dt

        request = self.factory.get('/foreign_news/')
        request.user = self.user
        self.add_session_to_request(request)

        view = ForeignNewsView()
        view.request = request
        view.get_foreign_news_data()

        # 各記事のconvert_utc_to_jst()が呼ばれた回数を確認
        self.assertEqual(mock_convert.call_count, 3)

        # 各記事の日付がループ処理で正しく変換されているか確認
        # mock_convert.call_args_list は、呼び出された引数のリストを持っている
        #例：mock_convert.call_args_list[0][0][0] は、1回目のconvert_utc_to_jst()呼び出しの引数を取得する
        self.assertEqual(mock_convert.call_args_list[0][0][0], "2025-03-30T12:00:00Z") #1回目の呼び出しは "2025-03-30T12:00:00Z" だったことを確認
        self.assertEqual(mock_convert.call_args_list[1][0][0], "2025-03-30T13:00:00Z") #2回目の呼び出しは "2025-03-30T13:00:00Z" だったことを確認
        self.assertEqual(mock_convert.call_args_list[2][0][0], "2025-03-30T14:00:00Z")


# NikkeiMedView のテスト
class NikkeiMedViewTests(TestCase):
    def setUp(self):
        # get_user_model() でユーザーモデルを取得してユーザー作成
        self.user = get_user_model().objects.create_user(username='user', password='pass')
        self.client.login(username='user', password='pass')
    
    # 異常系：ログインしていないとき、ログインページへリダイレクトされるか
    def test_redirect_if_not_logged_in(self):
        self.client.logout()
        response = self.client.get(reverse("news_app:nikkei_med"))
        self.assertRedirects(response, f'/accounts/login/?next={reverse("news_app:nikkei_med")}')


    # 正常系1：ページネーションが正しく機能しているか
    @patch('news_app.views.scraping_NikkeiMed')
    def test_view_returns_200_with_articles(self, mock_scraping):
        mock_scraping.return_value = [{'title': f'記事{i}', 'url': f'https://example.com/article{i}'} for i in range(15)]

        response = self.client.get(reverse('news_app:nikkei_med'))

        self.assertEqual(response.status_code, 200)
        self.assertIn('page_obj', response.context_data)

        # 10件表示されるページネーションの確認(1ページ目)
        self.assertEqual(len(response.context_data['page_obj']), 10)

    # 正常系2：ページネーションが正しく機能しているか
    @patch('news_app.views.scraping_NikkeiMed')
    def test_view_pagination_second_page(self, mock_scraping):
        # 15件あるので、2ページ目は5件になるはず
        mock_scraping.return_value = [{'title': f'記事{i}', 'url': f'https://example.com/article{i}'} for i in range(15)]

        response = self.client.get(reverse('news_app:nikkei_med') + '?page=2')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context_data['page_obj']), 5)

    # 異常系：スクレイピングが失敗した場合(空のリストを返すとき)、ビューがクラッシュしないか
    @patch("news_app.views.scraping_NikkeiMed")
    def test_view_handles_scraping_failure(self, mock_scraping):
        mock_scraping.return_value = []  # 空リストを返すように設定

        response = self.client.get(reverse("news_app:nikkei_med"))

        self.assertEqual(response.status_code, 200) # ビューがクラッシュしない
        self.assertIn("page_obj", response.context_data)
        self.assertEqual(len(response.context_data["page_obj"]), 0)  # 空の記事リストになってる


# ZiziMedView のテスト
class ZiziMedViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="user", password="pass")
        self.client.login(username="user", password="pass") # ログイン

    # 異常系：ログインしていないとき、ログインページへリダイレクトされるか
    def test_redirect_if_not_logged_in(self):
        self.client.logout() # ログアウト
        response = self.client.get(reverse("news_app:zizi_med"))
        self.assertRedirects(response, f"/accounts/login/?next={reverse('news_app:zizi_med')}")

    # 正常系1：ページネーションが正しく機能しているか
    @patch("news_app.views.scraping_ZiziMed")
    def test_view_returns_200_with_articles(self, mock_scraping):
        mock_scraping.return_value = [
            {"title": f"記事{i}", "url": f"https://example.com/article{i}"} for i in range(15)
        ]

        response = self.client.get(reverse("news_app:zizi_med"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("page_obj", response.context)
        # 記事リストが15件返る → 10件が1ページ目に表示
        self.assertEqual(len(response.context["page_obj"]), 10)

    # 正常系2：ページネーションが正しく機能しているか
    @patch("news_app.views.scraping_ZiziMed")
    def test_view_pagination_second_page(self, mock_scraping):
        mock_scraping.return_value = [
            {"title": f"記事{i}", "url": f"https://example.com/article{i}"} for i in range(15)
        ]
        
        response = self.client.get(reverse("news_app:zizi_med") + "?page=2")

        self.assertEqual(response.status_code, 200)
        self.assertIn("page_obj", response.context)
        self.assertEqual(len(response.context["page_obj"]), 5) # 15件 → 2ページ目は5件


    # 異常系：スクレイピング関数が空リストを返してもビューはクラッシュしない
    @patch("news_app.views.scraping_ZiziMed")
    def test_view_handles_scraping_failure(self, mock_scraping):
        mock_scraping.return_value = []

        response = self.client.get(reverse("news_app:zizi_med"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("page_obj", response.context)
        self.assertEqual(len(response.context["page_obj"]), 0)


# FavoriteListView のテスト

class FavoriteListViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="user", password="pass")
        self.client.login(username="user", password="pass")

    # 異常系：ログインしていないとき、ログインページへリダイレクトされるか
    def test_favorite_list_requires_login(self):
        self.client.logout() # ログアウト
        response = self.client.get(reverse("news_app:favorite_list"))
        self.assertRedirects(response, f"/accounts/login/?next={reverse('news_app:favorite_list')}")
    
    # 正常系1：お気に入り記事一覧が正しく表示されるか
    def test_favorite_list_view_shows_user_articles(self):
        # 自分の投稿記事5件＋他人の記事3件
        for i in range(5):
            Article.objects.create(user=self.user, article_title=f"記事{i}", article_url=f"https://example.com/{i}")

        other_user = get_user_model().objects.create_user(username="other", password="pass")
        for i in range(3):
            Article.objects.create(user=other_user, article_title=f"他人の記事{i}", article_url=f"https://other.com/{i}")

        response = self.client.get(reverse("news_app:favorite_list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "favorite_list.html")
        self.assertIn("page_obj", response.context)
        page_obj = response.context["page_obj"]

        # 自分の記事だけ表示される
        self.assertEqual(len(page_obj), 5) # 自分の記事5件  
        for article in page_obj:
            self.assertEqual(article.user, self.user) # 自分の記事だけがあるか

    # 正常系2：お気に入り記事一覧が正しくページネーションされるか
    def test_favorite_list_view_pagination(self):
        # 6件作ってページネーションを確認（1ページに5件）
        for i in range(6):
            Article.objects.create(user=self.user, article_title=f"記事{i}", article_url=f"https://example.com/{i}")

        response = self.client.get(reverse("news_app:favorite_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["page_obj"]), 5)  # 1ページ目は5件

        response2 = self.client.get(reverse("news_app:favorite_list") + "?page=2")
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(len(response2.context["page_obj"]), 1)  # 2ページ目は1件