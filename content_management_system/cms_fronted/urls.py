from django.urls import path
from .views import *


urlpatterns = [
    path('', index.as_view(), name='index'),
    path('user_login/', LoginView.as_view(), name='user_login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('view_more/<int:id>', ViewMore.as_view(), name='view_more'),
]
