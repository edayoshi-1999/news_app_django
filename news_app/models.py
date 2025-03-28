from django.db import models
from accounts.models import CustomUser

class Article(models.Model):
    user = models.ForeignKey(CustomUser, verbose_name="ユーザー", on_delete=models.PROTECT)

    article_title = models.CharField(verbose_name="記事タイトル", blank=True, null=True)
    article_url = models.URLField(verbose_name="記事URL", blank=True, null=True, unique=True)
    article_img_url = models.URLField(verbose_name="記事画像URL", blank=True, null=True)
    memo = models.CharField(verbose_name="メモ", blank=True, null=True)

    published_at = models.DateField(verbose_name="記事公開日時", blank=True, null=True)
    created_at = models.DateTimeField(verbose_name="作成日時" ,auto_now_add=True)
    updated_at = models.DateTimeField("更新日時", auto_now=True)
    
    class Meta:
        verbose_name_plural = "article"

    def __str__(self):
        return self.article_title or "(タイトルなし)"