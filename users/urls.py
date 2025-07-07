from django.urls import path
from .views import (
    UserLoginView,
    UserLogoutView,
    UserRegisterView,
    UserProfileView,
    UserProfileEditView, UserListView, block_user, unblock_user,
)

app_name = "users"

urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLogoutView.as_view(), name="logout"),  # ← выход через POST
    path("register/", UserRegisterView.as_view(), name="register"),
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("profile/edit/", UserProfileEditView.as_view(), name="profile_edit"),
    path("all/", UserListView.as_view(), name="user-list"),
    path("<int:pk>/block/", block_user, name="block-user"),
    path("<int:pk>/block/", block_user, name="block-user"),
    path("<int:pk>/unblock/", unblock_user, name="unblock-user"),
]
