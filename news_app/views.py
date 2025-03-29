from django.shortcuts import render
from django.views import generic
from django.core.paginator import Paginator
from .services.scrapingNikkeiMed import scraping_NikkeiMed
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Article
from .forms import AddFavoriteForm
from django.urls import reverse_lazy
import logging
from django.contrib import messages
from datetime import datetime
from django.shortcuts import get_object_or_404


logger = logging.getLogger(__name__)

# Djangoの認証ミックスインを使って、ログインしていないユーザーは403エラーを返す
class OnlyYouMixin(UserPassesTestMixin):
    raise_exception = True # 認証エラー時に403を返す

    def test_func(self):
        # ログインユーザーが記事の所有者かどうかをチェック
        # self.request.userはログインユーザー
        # URLに含まれるpkを使って、Articleモデルから記事を取得。取得できなかった場合は404エラーを返す。
        article = get_object_or_404(Article, pk=self.kwargs['pk'])
        return self.request.user == article.user

# トップページのビュー
class IndexView(generic.TemplateView):
    template_name = "index.html"

# 国際ニュースのビュー
class ForeignNewsView(LoginRequiredMixin, generic.TemplateView):
    template_name = "foreign_news.html"

# 日経メディカルのビュー
class NikkeiMedView(LoginRequiredMixin, generic.TemplateView):
    template_name = "nikkei_med.html"

    # テンプレートに記事情報を渡す
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['articles'] = scraping_NikkeiMed()

        # 記事一覧を取得
        article_list = scraping_NikkeiMed()

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

        # published_atの初期値を取得し、適切な形へ変換。エラーを回避するため。
        # 例: 2023/10/01　→　2023-10-01 に変換
        raw_date = self.request.GET.get('published_at')
        published_date = None

        if raw_date:
            try:
                published_date = datetime.strptime(raw_date, "%Y/%m/%d").date()
            except ValueError as e:
                logger.error(f"日付のパースに失敗しました（入力: '{raw_date}'）: {e}")

        return {
            'article_title': self.request.GET.get('article_title'),
            'article_url': self.request.GET.get('article_url'),
            'article_img_url': self.request.GET.get('article_img_url'),
            'published_at': published_date,
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
        logger.info("★ form_valid updateが() 呼ばれた！")
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
        logger.info(f"★ post() 手動で delete() 呼びます）")
        return self.delete(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        logger.info("★ delete() 呼ばれた！")
        messages.success(self.request, "お気に入り記事を削除しました")
        return super().delete(request, *args, **kwargs)
