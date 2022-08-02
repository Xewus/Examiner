from django.urls import path

from . import views

app_name = 'questions'

urlpatterns = [
    path('', views.index, name='index'),
    path('rating/', views.rating, name='rating'),
    path('my_results/', views.my_results, name='my_results'),
    path('questions/', views.get_question, name='questions'),
    path('answer/<int:question_pk>', views.add_answer, name='answers'),
    path('finish_test/', views.to_finish_test, name='finish_test'),
]
