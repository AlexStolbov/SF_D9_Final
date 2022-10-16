from django import template

register = template.Library()

SWEAR_WORDS = [
    'ругань1',
    'ругань2',
    'ругань3',
]


@register.filter()
def censor(value):
    """
    Заменяет нецензурные слова на *
    """
    res = value

    if type(value) == str:
        for swear_word in SWEAR_WORDS:
            res = res.replace(swear_word, '****')
            res = res.replace(swear_word.capitalize(), '****')
    return res


@register.filter()
def show_categories(categories):
    """
    Формирует строку из имен категорий
    categories: post.category
    """
    categories_name = list(map(lambda cat: cat.name, categories.all()))
    return ', '.join(categories_name)
