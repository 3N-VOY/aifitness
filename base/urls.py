from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('video_feed', views.video_feed, name='video_feed'),
    path('upload_video', views.upload_video, name='upload_video'),
]
