import json
import os

from django.apps.registry import Apps
from django.conf import settings
from django.db import migrations
from recipes.models import Ingredient, Tag

DATA_DIR = os.path.join(settings.BASE_DIR.parent, "data")


def add_ingredient_data(apps: Apps, *args, **kwargs):
    with open("data/ingredients.json", "rt", encoding="utf-8") as f:
        data = json.load(f)
        for row in data:
            Ingredient.objects.create(**row)


def delete_ingredient_data(apps: Apps, *args, **kwargs):
    with open("data/ingredients.json", "rt", encoding="utf-8") as f:
        data = json.load(f)
        for row in data:
            names = row["name"]
            measurement_units = row["measurement_units"]
            Ingredient.objects.filter(
                name__in=names, measurement_unit__in=measurement_units
            ).delete()


def add_tags_data(apps: Apps, *args, **kwargs):
    with open("data/tag.json", "rt", encoding="utf-8") as f:
        data = json.load(f)
        for row in data:
            Tag.objects.create(**row)


def delete_tags_data(apps: Apps, *args, **kwargs):
    with open("data/yag.json", "rt", encoding="utf-8") as f:
        data = json.load(f)
        for row in data:
            names = row["name"]
            Tag.objects.filter(name__in=names).delete()


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("recipes", "0002_auto_20220817_1551"),
    ]
    operations = [
        migrations.RunPython(
            add_ingredient_data, reverse_code=delete_ingredient_data
        ),
        migrations.RunPython(add_tags_data, reverse_code=delete_tags_data),
    ]
