"""
Импорт json из папки data/.

"""
import json

from django.core.management.base import BaseCommand

from recipes.models import Ingridient


class Command(BaseCommand):
    DONE_MESSAGE = "Данные  перенесены в таблицу Ingridient."
    ERROR_MESSAGE = "Ошибка - {error}, проблема с данными - {row}."
    def handle(self, *args, **options):
        
        with open("data/ingredients.json", "rt") as f:
            data = json.load(f)
            for row in data:
                try:
                    Ingridient.objects.create(**row)                
                except Exception as error:
                    print(self.ERROR_MESSAGE.format(error=error, row=row))
            print(self.DONE_MESSAGE)
