"""
Тип поста, «статья» или «новость»;
"""
post_type_article = "ART"
post_type_news = "NWS"
POST_TYPE = [
    (post_type_article, "Article"),
    (post_type_news, "News"),
]


def get_post_type_name(post_type):
    """
    Возвращает текстовое наименование типа статьи
    """
    result = ''
    for el in POST_TYPE:
        if el[0] == post_type:
            result = el[1]
            break
    return result
