# этот файл создан, чтобы импортировать ф-ю save_csv_products
# в админку и обычные view ф-и
# это должен быть промежуточный файл, чтобы не было импортов
# из админки в обычные view ф-и или наоборот
from csv import DictReader
from io import TextIOWrapper

from shopapp.models import Product


def save_csv_products(file, encoding):
    csv_file = TextIOWrapper(file, encoding=encoding)

    reader = DictReader(csv_file)
    # каждая строка (row) будет словарём

    products = [
        Product(**row)
        for row in reader
    ]

    # Массово вставим объекты
    Product.objects.bulk_create(products)

    return products
