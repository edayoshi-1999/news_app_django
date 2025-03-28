from django.shortcuts import render
from django.views import generic
from django.core.paginator import Paginator
from .services.scrapingNikkeiMed import scraping_NikkeiMed
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Article
from .forms import AddFavoriteForm
from django.urls import reverse_lazy
import logging
from django.contrib import messages
from datetime import datetime

logger = logging.getLogger(__name__)

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

    # バリデーションを通った場合の処理
    def form_valid(self, form):
        article = form.save(commit=False)
        article.user = self.request.user
        article.save()
        messages.success(self.request, "お気に入り記事を追加しました")
        return super().form_valid(form)
    
    # バリデーションを通らなかった場合の処理
    def form_invalid(self, form):
        messages.error(self.request, "お気に入り記事の追加に失敗しました")
        return super().form_invalid(form)
    
    # フォームに初期値をセット
    def get_initial(self):

        # published_atの初期値を取得し、変換
        # 例: 2023/10/01　→　2023-10-01 に変換
        raw_date = self.request.GET.get('published_at')
        published_date = None

        if raw_date:
            try:
                published_date = datetime.strptime(raw_date, "%Y/%m/%d").date()
            except ValueError:
                pass

        return {
            'article_title': self.request.GET.get('article_title'),
            'article_url': self.request.GET.get('article_url'),
            'article_img_url': self.request.GET.get('article_img_url'),
            'published_at': published_date,
        }
    

# お気に入り記事更新のビュー
class UpdateFavoriteView(LoginRequiredMixin, generic.UpdateView):
    model = Article
    template_name = "update_favorite.html"
    form_class = AddFavoriteForm
    success_url = reverse_lazy("news_app:favorite_list")

    # バリデーションを通った場合の処理
    def form_valid(self, form):
        messages.success(self.request, "お気に入り記事を更新しました")
        return super().form_valid(form)
    
    # バリデーションを通らなかった場合の処理
    def form_invalid(self, form):
        messages.error(self.request, "お気に入り記事の更新に失敗しました")
        return super().form_invalid(form)

