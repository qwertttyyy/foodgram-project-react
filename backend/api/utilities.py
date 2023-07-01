import os
from io import BytesIO

from django.db.models import Sum
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.rl_settings import TTFSearchPath

from backend.settings import FONTS_PATH
from recipes.models import RecipeIngredient


def create_shopping_list(shopping_cart):
    grouped_ingredients = (
        RecipeIngredient.objects.filter(recipe__in=shopping_cart)
        .values('ingredient__name', 'ingredient__measurement_unit')
        .annotate(amount_sum=Sum('amount'))
    )

    shopping_list = {
        ingredient['ingredient__name']: '%s %s'
        % (
            ingredient['amount_sum'],
            ingredient['ingredient__measurement_unit'],
        )
        for ingredient in grouped_ingredients
    }

    return shopping_list


def generate_shopping_list_pdf(shopping_cart):
    TTFSearchPath + (str(FONTS_PATH).replace(os.sep, '/'),)
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    font = 'Consolas Bold'
    pdfmetrics.registerFont(TTFont(font, 'consolab.ttf'))
    pdf.setFont(font, 18)

    pdf.drawCentredString(300, 750, 'Список покупок')

    pdf.setFont(font, 12)

    x = 80
    y = 700

    for count, (item, amount) in enumerate(shopping_cart.items()):
        count += 1
        dots = 70 - (
            len(str(count)) + len(item.capitalize()) + len(amount) + 4
        )
        line = f'{count}. {item.capitalize()} {"." * dots} {amount}'
        pdf.drawString(x, y, line)
        y -= 25

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer
