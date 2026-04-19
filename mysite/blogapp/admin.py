from django.contrib import admin

from .models import Article


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    # Отображаемые поля
    list_display = 'id', 'title', 'body', 'published_at'
