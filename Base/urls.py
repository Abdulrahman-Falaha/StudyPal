from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logoutUser, name="logout"),
    path("register/", views.register_Page, name="register"),
    path("profile/<str:pk>", views.userProfile, name="profile_page"),
    path("", views.home, name="home"),
    path("room/<str:pk>/", views.room, name="room"),
    path("create_room/", views.createRoom, name="create_page"),
    path("update_room/<str:pk>/", views.updateRoom, name="update_page"),
    path("delete_room/<str:pk>/", views.deleteRoom, name="delete_page"),
    path("delete_message/<str:pk>/", views.deleteMessage, name="delete_message"),
    path("update_user/", views.updateUser, name="update_user_page"),
    path("topics/", views.topicsPage, name="topics_page"),
    path("activity/", views.activityPage, name="activity_page"),
]
