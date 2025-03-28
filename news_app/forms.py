from django import forms
from .models import Article
from django.core.exceptions import ValidationError

class AddFavoriteForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['article_title', 'article_url', 'article_img_url', 'published_at', 'memo']  # 'user' はビューで設定
        widgets = {
            'memo': forms.Textarea(attrs={'rows': 3, 'placeholder': 'メモがあればどうぞ…'}),
        }

    # 記事URLの重複チェック
    def clean_article_url(self):
        url = self.cleaned_data.get('article_url')
        if Article.objects.filter(article_url=url).exists():
            raise ValidationError("この記事はすでに登録されています。")
        return url