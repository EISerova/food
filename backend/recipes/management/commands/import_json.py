"""
Импорт json из папки data/.

"""
import json

from django.core.management.base import BaseCommand

from recipes.models import Ingredient, Tag


class Command(BaseCommand):
    DONE_MESSAGE_INGREDIENT = "Данные  перенесены в таблицу Ingridient."
    DONE_MESSAGE_TAG = "Данные  перенесены в таблицу Tag."
    ERROR_MESSAGE = "Ошибка - {error}, проблема с данными - {row}."

    def handle(self, *args, **options):

        with open("data/ingredients.json", "rt") as f:
            data = json.load(f)
            for row in data:
                try:
                    Ingredient.objects.create(**row)
                except Exception as error:
                    print(self.ERROR_MESSAGE.format(error=error, row=row))
            print(self.DONE_MESSAGE_INGREDIENT)

        with open("data/tag.json", "rt") as f:
            data = json.load(f)
            for row in data:
                try:
                    Tag.objects.create(**row)
                except Exception as error:
                    print(self.ERROR_MESSAGE.format(error=error, row=row))
            print(self.DONE_MESSAGE_TAG)
