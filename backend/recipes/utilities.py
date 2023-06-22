import os

from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.rl_settings import TTFSearchPath

from api.models import RecipeIngredient
from recipes.constants import CACHE_PATH, FONTS_PATH


def create_shopping_list(shopping_cart):
    shopping_list = {}

    for recipe in shopping_cart:
        recipe_ingredients = RecipeIngredient.objects.filter(recipe=recipe)
        for recipe_ingredient in recipe_ingredients:
            ingredient = recipe_ingredient.ingredient
            if ingredient in shopping_list:
                shopping_list[ingredient] += recipe_ingredient.amount
            else:
                shopping_list[ingredient] = recipe_ingredient.amount

    shopping_list = {
        ingredient.name: '%s %s' % (amount, ingredient.measurement_unit)
        for ingredient, amount in shopping_list.items()
    }

    return shopping_list


def generate_shopping_list_pdf(shopping_cart, filename):
    TTFSearchPath + (str(FONTS_PATH).replace(os.sep, '/'),)
    pdf = canvas.Canvas(os.path.join(CACHE_PATH, filename), pagesize=letter)
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
