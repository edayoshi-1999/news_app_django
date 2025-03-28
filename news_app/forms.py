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
        qs = Article.objects.filter(article_url=url)

        # 編集中（UpdateViewなど）の場合、自分自身は除外
        # これを書くことで、編集するときに重複チェックを避けられる。
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        # 重複チェック
        if qs.exists():
            raise ValidationError("この記事はすでに登録されています。")
        
        return url