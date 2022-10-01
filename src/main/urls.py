from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('add/<int:film_id>', views.add_comment, name='add_comment'),
    path('comments/<int:film_id>', views.comments, name='show_comments')
]
