from django.urls import path
from . import views

app_name = 'learning'

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('search/', views.search, name='search'),
    path('panel/', views.knowledge_panel, name='knowledge_panel'),
    path('panel/mindmap/', views.knowledge_panel_mindmap, name='knowledge_panel_mindmap'),
    path('topic/create/', views.topic_create, name='topic_create'),
    path('topic/<int:topic_id>/', views.topic_detail, name='topic_detail'),
    path('topic/<int:topic_id>/edit/', views.topic_update, name='topic_update'),
    path('topic/<int:topic_id>/delete/', views.topic_delete, name='topic_delete'),
]
