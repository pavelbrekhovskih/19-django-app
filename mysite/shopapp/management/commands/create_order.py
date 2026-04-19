from typing import Sequence

from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db import transaction

from shopapp.models import Order, Product


class Command(BaseCommand):
    """
    Creates new order.
    """

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Create order with products")
        user = User.objects.get(username="admin")
        products: Sequence[Product] = Product.objects.only('id').all() # Здесь вернётся queryset
        order, created = Order.objects.get_or_create(
            delivery_adress="ul Belgee, d 12",
            promocode="SALE5",
            user=user
        )

        # Здесь пр-т запрос товаров
        for product in products:
            order.products.add(product)
        order.save()

        self.stdout.write(f"Created order {order}")
        self.stdout.write(self.style.SUCCESS("Order created"))
