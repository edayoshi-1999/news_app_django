from django.shortcuts import render
from django.views import generic
from django.core.paginator import Paginator
from .services.scrapingNikkeiMed import scraping_NikkeiMed
from .services.scrapingZiziMed import scraping_ZiziMed
from .services.newsAPI import fetch_news_from_api
from .services.utils import parse_date, convert_utc_to_jst
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Article
from .forms import AddFavoriteForm
from django.urls import reverse_lazy
import logging
from django.contrib import messages
from datetime import datetime, timezone, timedelta
from django.shortcuts import get_object_or_404
from django.contrib.auth.views import redirect_to_login


logger = logging.getLogger(__name__)

# Djangoの認証ミックスインを使って、ログインしていないユーザーは403エラーを返す
class OnlyYouMixin(UserPassesTestMixin):
    raise_exception = True # 認証エラー時に403を返す

    def test_func(self):
        # 未ログインの場合は False を返す（→ djangoが自動でhandle_no_permission()を呼び出す。）
        if not self.request.user.is_authenticated:
            return False
        
        # ログインユーザーが記事の所有者かどうかをチェック
        # URLに含まれるpkを使って、Articleモデルから記事を取得。取得できなかった場合は404エラーを返す。
        # self.request.userはログインユーザー
        article = get_object_or_404(Article, pk=self.kwargs["pk"])
        return self.request.user == article.user

    # test_func()でFalseが返された場合に呼ばれる。つまり、以下の2通りの呼ばれ方がある
    # request.user.is_authenticated が False ⟶ return False
    # request.user.is_authenticated が True ⟶ return super().handle_no_permission()でFalse
    # つまり、未ログインの場合はログインページへリダイレクトし、
    # ログイン済みだが所有者でない場合は403エラーを返す。
    def handle_no_permission(self):
        # 未ログインならログインページへリダイレクト
        if not self.request.user.is_authenticated:
            return redirect_to_login(self.request.get_full_path())

        # ログイン済みだが所有者でない場合は 403
        return super().handle_no_permission()

# トップページのビュー
class IndexView(generic.TemplateView):
    template_name = "index.html"

# 国際ニュースのビュー
class ForeignNewsView(LoginRequiredMixin, generic.TemplateView):
    template_name = "foreign_news.html"

    # テンプレートに記事情報を渡す
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 記事一覧を取得
        article_list = self.get_foreign_news_data()

        # ページネーション処理（1ページに10記事）
        paginator = Paginator(article_list, 10)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        # テンプレートに渡す
        context["page_obj"] = page_obj

        return context
    

    # 初回だけAPI取得（セッションに保存）
    # シングルページアプリケーションのように、毎回APIを叩くのではなく、
    # セッションに保存しておくことで、ページ遷移時にAPIを叩かないようにする。
    def get_foreign_news_data(self):
        # セッションに保存されていない場合はAPIを叩く
        # セッションに保存されている場合は、セッションから取得する。
        if "foreign_news_data" not in self.request.session:
            article_list = fetch_news_from_api()
            
            # published_at(=article_listの2番目の要素=article[1])を日本時間に変換
            for article in article_list:
                article[1] = convert_utc_to_jst(article[1])

            self.request.session["foreign_news_data"] = article_list
        return self.request.session["foreign_news_data"]
    


# 日経メディカルのビュー
class NikkeiMedView(LoginRequiredMixin, generic.TemplateView):
    template_name = "nikkei_med.html"

    # テンプレートに記事情報を渡す
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 記事一覧を取得
        article_list = scraping_NikkeiMed()

        # ページネーション処理（1ページに10記事）
        paginator = Paginator(article_list, 10)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        # テンプレートに渡す
        context["page_obj"] = page_obj

        return context

# 時事メディカルのビュー
class ZiziMedView(LoginRequiredMixin, generic.TemplateView):
    template_name = "zizi_med.html"

    # テンプレートに記事情報を渡す
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 記事一覧を取得
        article_list = scraping_ZiziMed()

        # ページネーション処理（1ページに10記事）
        paginator = Paginator(article_list, 10)
        page_number = self.request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        # テンプレートに渡す
        context["page_obj"] = page_obj

        return context

# お気に入り記事一覧のビュー
class FavoriteListView(LoginRequiredMixin ,generic.ListView):
    model = Article
    template_name = "favorite_list.html"
    paginate_by = 5

    def get_queryset(self):
        articles = Article.objects.filter(user=self.request.user).order_by("-created_at")
        return articles
    
# お気に入り記事追加のビュー
class AddFavoriteView(LoginRequiredMixin, generic.FormView):
    model = Article
    template_name = "add_favorite.html"
    form_class = AddFavoriteForm
    success_url = reverse_lazy("news_app:favorite_list")

    # フォームに user を渡す
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    # フォームに初期値をセット
    def get_initial(self):

        # published_at の初期値を取得し、datetime型に変換する。
        published_at = parse_date(self.request.GET.get('published_at'))

        return {
            'article_title': self.request.GET.get('article_title'),
            'article_url': self.request.GET.get('article_url'),
            'article_img_url': self.request.GET.get('article_img_url'),
            'published_at': published_at,
        }  
    
    # バリデーションを通った場合の処理
    def form_valid(self, form):
        article = form.save(commit=False)
        article.user = self.request.user # モデルにユーザーをセット
        article.save()
        messages.success(self.request, "お気に入り記事を追加しました")
        return super().form_valid(form)
    
    # バリデーションを通らなかった場合の処理
    def form_invalid(self, form):
        messages.error(self.request, "お気に入り記事の追加に失敗しました")
        return super().form_invalid(form)
    
    
    

# お気に入り記事更新のビュー
class UpdateFavoriteView(LoginRequiredMixin, OnlyYouMixin, generic.UpdateView):
    model = Article
    template_name = "update_favorite.html"
    form_class = AddFavoriteForm
    success_url = reverse_lazy("news_app:favorite_list")

    # バリデーションを通った場合の処理
    def form_valid(self, form):
        messages.success(self.request, "お気に入り記事を更新しました")
        # logger.info("★ form_valid updateが() 呼ばれた！")
        return super().form_valid(form)
    
    # バリデーションを通らなかった場合の処理
    def form_invalid(self, form):
        messages.error(self.request, "お気に入り記事の更新に失敗しました")
        return super().form_invalid(form)

# お気に入り記事削除のビュー
class DeleteFavoriteView(LoginRequiredMixin, OnlyYouMixin, generic.DeleteView):
    model = Article
    template_name = "delete_favorite.html"
    success_url = reverse_lazy("news_app:favorite_list")

    # messageを表示するために、postメソッドをオーバーライドしてdeleteメソッドを呼び出す
    # これをしないと、deleteメソッドが呼ばれない。理由は不明。
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        # logger.info(f"★ post() 手動で delete() 呼びます）")
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        # logger.info("★ delete() 呼ばれた！")
        messages.success(self.request, "お気に入り記事を削除しました")
        return super().delete(request, *args, **kwargs)
