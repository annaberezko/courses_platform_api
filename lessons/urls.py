from django.urls import path

from lessons.views import LessonsListAPIView, LessonAPIView, MaterialAPIView, MaterialDetailAPIView, \
    QuestionsListAPIView, QuestionAPIView, OptionAPIView

app_name = 'lessons'

urlpatterns = [
    path('', LessonsListAPIView.as_view(), name='lesson-list'),
    path('<int:pk>/', LessonAPIView.as_view(), name='lesson-detail'),
    path('<int:pk>/tests/', QuestionsListAPIView.as_view(), name='lesson-test'),
    path('<int:pk>/tests/<int:test_pk>/', QuestionAPIView.as_view(), name='lesson-test-detail'),
    path('<int:pk>/tests/<int:test_pk>/<int:option_pk>/', OptionAPIView.as_view(), name='option-detail'),
    path('<int:pk>/materials/', MaterialAPIView.as_view(), name='add-material'),
    path('<int:pk>/materials/<int:material_pk>/', MaterialDetailAPIView.as_view(), name='material-detail'),
    ]
