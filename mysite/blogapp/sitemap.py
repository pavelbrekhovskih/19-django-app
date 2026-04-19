from django.contrib.sitemaps import Sitemap

from .models import Article

class BlogSiteMap(Sitemap):
    changefreq = 'never' # (always, hourly, daily, weekly, monthly, yearly)
    priority = 0.5  # 1 самая главная страница

    def items(self):
        return Article.objects.filter(published_at__isnull=False).order_by('-published_at')[:5]

    # метод, так как данные будут меняться
    def lastmod(self, obj: Article):
        return obj.published_at
