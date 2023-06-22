import csv
import os

import django
from django.apps import apps
from django.core.management.base import BaseCommand
from django.db.utils import OperationalError

from backend.settings import BASE_DIR

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

data_path = BASE_DIR / 'data'


class Command(BaseCommand):
    """Кастомная команда записи данных из csv файлов в базу данных
    шаблон: python manage.py writecsv appname.Modelname csv_file_name
    """

    def add_arguments(self, parser):
        parser.add_argument(
            'model',
            help='Модель для которой записываются данные (appname.ModelName)',
        )
        parser.add_argument('csv_file', help='Имя csv файла')

    def handle(self, *args, **options):
        model_name = options['model']
        file_name = options['csv_file'] + '.csv'

        file_path = os.path.join(data_path, file_name)
        model = apps.get_model(model_name)

        try:
            with open(file_path, 'r', encoding='utf-8') as csv_file:
                reader = csv.reader(csv_file)

                next(reader)

                for row in reader:
                    obj = model()
                    for field_index, field in enumerate(row):
                        # получает имя поля, пропускает поле id
                        field_name = obj._meta.fields[field_index + 1].attname
                        # сохраняет значение из файла в поле
                        setattr(obj, field_name, field)
                    obj.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f'Данные успешно записаны из {file_path} в {model_name}',
                ),
            )
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Файл {file_name} не найден.'))
        except OperationalError:
            self.stdout.write(
                self.style.ERROR(
                    'Вы попытались заполнить таблицу со '
                    'связанным полем, но не заполнили внешнюю.',
                ),
            )
