import logging
from pickle import FALSE
from timeit import default_timer
from csv import DictWriter

from django.contrib.auth.models import Group
from django.shortcuts import render, redirect, reverse, get_object_or_404  # помощники
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .common import save_csv_products
from .forms import ProductForm, GroupForm
from .models import Product, Order, ProductImage
from .serializers import ProductSerializer

log = logging.getLogger(__name__)


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter
    ]

    search_fields = ['name', 'description']

    filterset_fields = [
        'name',
        'description',
        'price',
        'discount',
        'archived'
    ]

    ordering_fields = [
        'pk',
        'name',
        'price',
        'discount',
    ]

    @method_decorator(cache_page(60 * 2))
    def list(self, *args, **kwargs):
        # print("-------Hello Products List-----------")
        return super().list(*args, **kwargs)


    @action(methods=['get'], detail=False)
    def download_csv(self, request: Request):
        # Подготовим http ответ с csv файлом
        response = HttpResponse(content_type='text/csv')
        filename = 'products-export.csv'
        response["Content-Disposition"] = f"attachement; filename={filename}"
        # фильтрация произойдёт с учётом всех пар-в класса (см. выше)
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            'name',
            'description',
            'price',
            'discount',
        ]
        # чтобы не загружать все поля модели
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for product in queryset:
            writer.writerow({
                field: getattr(product, field)
                for field in fields
            })

        return response

    @action(methods=['post'], detail=False, parser_classes=[MultiPartParser])
    def upload_csv(self, request: Request):
        products = save_csv_products(
            request.FILES['file'].file,
            encoding=request.encoding
        )

        serializer = self.get_serializer(products, many=True)

        return Response(serializer.data)


class ShopIndexView(View):
    # @method_decorator(cache_page(60 * 2)) # в секундах
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ('Laptop', 1999),
            ('Desktop', 2999),
            ('Smartphone', 5999),
        ]
        context = {
            "time_running": default_timer(),
            "products": products,
            "items": 2
        }
        log.debug('Products for shop index: %s', products)
        log.info('Rendering shop index')

        # Если исп-ся кешир-е, это выведется в консоль 1 раз
        print('shop index context', context)

        return render(request, 'shopapp/shop-index.html', context=context)


class GroupsListView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        context = {
            "form": GroupForm(),
            "groups": Group.objects.prefetch_related('permissions').all(),
        }
        return render(request, 'shopapp/groups-list.html', context=context)

    def post(self, request: HttpRequest):
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()

        return redirect(request.path)  # redirect избавит польз-ля от ошибки при перезагрузке страницы,
        # если сделать render, то польз-ль сможет снова опубликовать ту же форму
        # если redirect, то форма не сохранится в текущем запросе
        # return self.get(request)


class ProductDetailsView(DetailView):
    template_name = 'shopapp/product-details.html'
    # model = Product  # вытаскиваем данные из БД
    queryset = Product.objects.prefetch_related("images")  # чтобы images подгр-сь заранее
    context_object_name = "product"


class ProductsListView(ListView):
    template_name = 'shopapp/products-list.html'
    # model = Product  # вытаскиваем данные из БД все
    context_object_name = 'products'
    queryset = Product.objects.filter(archived=False)


# class ProductCreateView(UserPassesTestMixin, CreateView):
class ProductCreateView(CreateView):
    # def test_func(self):
    # return self.request.user.groups.filter(name="secret-group").exists()
    # return self.request.user.is_superuser

    model = Product
    # fields = "name", "price", "description", "discount", "preview"
    form_class = ProductForm  # - можно использовать вместо написанного выше fields = ...
    success_url = reverse_lazy("shopapp:products_list")


class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    # fields = "name", "price", "description", "discount", "preview"
    template_name_suffix = "_update_form"

    # по self.object.pk будет доступен pk текущего обновлённого объекта
    def get_success_url(self):
        return reverse("shopapp:product_details",
                       kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist("images"):
            ProductImage.objects.create(
                product=self.object,
                image=image
            )

        return response


class ProductDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy("shopapp:products_list")

    # архивирование вместо удаления
    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()  # не забываем
        return HttpResponseRedirect(success_url)


class OrdersListView(LoginRequiredMixin, ListView):
    # т.к связ-е сущности, то исп-м queryset (можно без all())
    queryset = (
        Order.objects.all()
        .select_related("user")
        .prefetch_related("products")
    )


class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = ["shopapp:view_order"]
    # т.к связ-е сущности, то исп-м queryset без all()
    queryset = (
        Order.objects
        .select_related("user")
        .prefetch_related("products")
    )


class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        cache_key = 'products_data_export'
        products_data = cache.get(cache_key)

        if products_data is None:
            products = Product.objects.order_by("pk").all()
            products_data = [
                {
                    "pk": product.pk,
                    "name": product.name,
                    "price": product.price,
                    "archived": product.archived

                }
                for product in products
            ]
            cache.set(cache_key, products_data, 300)
        # elem = products_data[0]
        # name = elem['naem']

        return JsonResponse({"products": products_data})
