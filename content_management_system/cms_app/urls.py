from django.urls import path
from .views import *

urlpatterns = [
    path('login/', LoginAPI.as_view(), name='login'), 
    path('users/', BaseUserView.as_view()), 
    path('user/<uuid:uuid>', BaseUserDetail.as_view()),
    path('blogs/', BlogView.as_view()),
    path('blog/<int:id>', BlogDetail.as_view()),
    path('likes/', LikeView.as_view()),
    path('like/<int:id>', LikeDetail.as_view()),
]
