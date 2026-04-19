from django.contrib.syndication.views import Feed
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.urls import reverse, reverse_lazy

from .models import Article


class ArticlesListView(ListView):
    queryset = (
        Article.objects
        .filter(published_at__isnull=False)
        .order_by('-published_at')
    )


class ArticlesDetailView(DetailView):
    model = Article


class LatestArticlesFeed(Feed):
    title = 'Blog articles (latest)'
    description = 'Updates on changes and editions blog articles'
    link = reverse_lazy('blogapp:articles')  # Ссылка на дом-ю страницу

    def items(self):
        '''
        Реализует получение информации о статьях или других объектах,
        которые мы хотим возвращать в списке ленты
        (здесь только 5 свежих статей)
        '''
        return (
            Article.objects
            .filter(published_at__isnull=False)
            .order_by('-published_at')[:5]
        )

    def item_title(self, item: Article):
        '''
        Метод для получения заголовков из элементов списка
        '''
        return item.title

    def item_description(self, item: Article):
        return item.body[:200]
