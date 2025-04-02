from django.urls import path
from . import views 
urlpatterns = [
    path('', views.home, name='home'),
    path('chat/<uuid:chat_id>/', views.chat_room, name='chat_room'),  
    path('chat/<uuid:chat_id>/delete/', views.delete_chat, name='delete_chat'),
    path('chat/<uuid:chat_id>/status/', views.check_chat_status, name='check_chat_status')

]


