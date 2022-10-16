from django.urls import path
from .views import PostsList, PostsListSearch, NewsDetail, PostCreate, PostEdit, PostDelete

urlpatterns = [

   path('', PostsList.as_view(), name='post_list'),
   path('search/', PostsListSearch.as_view()),
   path('<int:id>', NewsDetail.as_view(), name='post_detail'),
   # News create
   path('news/create/', PostCreate.as_view(), name='news_create'),
   # Article create
   path('article/create/', PostCreate.as_view(), name='article_create'),
   # News edit
   path('news/<int:pk>/edit/', PostEdit.as_view(), name='news_edit'),
   # Article edit
   path('article/<int:pk>/edit/', PostEdit.as_view(), name='article_edit'),
   # News delete
   path('news/<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
   # Article delete
   path('article/<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
]
