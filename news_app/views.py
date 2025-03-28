from django.shortcuts import render
from django.views import generic
from django.core.paginator import Paginator
from .services.scrapingNikkeiMed import scraping_NikkeiMed


# Create your views here.
class IndexView(generic.TemplateView):
    template_name = "index.html"

class ForeignNewsView(generic.TemplateView):
    template_name = "foreign_news.html"

class NikkeiMedView(generic.TemplateView):
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