# weblog_project/weblog_app/urls.py
from django.urls import path
from . import views

# Create your app urls here.
urlpatterns = [

    path("", views.index, name="index"),
    path("welcome-message/", views.welcome_message, name="welcome_message"),
    path("sign-buttons/", views.sign_buttons, name="sign_buttons"),
    path("sign-up/", views.sign_up, name="sign_up"),
    path("sign-in/", views.sign_in, name="sign_in"),
    path("sign-up-form/", views.sign_up_form, name="sign_up_form"),
    path("sign-in-form/", views.sign_in_form, name="sign_in_form"),
    path("welcome/", views.welcome, name="welcome"),
    path("home/", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.log_out, name="logout"),
    path("login/", views.login_required_page, name="login_required_page"),

    # Profile
    path("profile/", views.profile, name="profile"),
    path("profile/update-profile/", views.update_profile, name="update_profile"),
    path("profile/update-picture/", views.update_picture, name="update_picture"),
    path("profile/delete-or-cancel/", views.delete_or_cancel, name="delete_or_cancel"),
    path("profile/remove-picture/", views.remove_picture, name="remove_picture"),
    path("profile/cancel-action/", views.cancel_action, name="cancel_action"),

    # Categories
    path("categories/", views.categories, name="categories"),
    path('add_category/', views.add_category, name='add_category'),
    path("categories/edit-<int:pk>/", views.category_edit, name="category_edit"),
    path("categories/delete-<int:pk>/", views.category_delete, name="category_delete"),
    path("category_detail-<int:pk>/", views.category_detail, name="category_detail"),

    # Tags
    path("tags/", views.tags, name="tags"),
    path("tag_detail-<int:pk>/", views.tag_detail, name="tag_detail"),
    path("tag_edit-<int:pk>/", views.tag_edit, name="tag_edit"),
    path("tag_delete-<int:pk>/", views.tag_delete, name="tag_delete"),
    path('add_tag/', views.add_tag, name='add_tag'),

    # Comments
    path("comments/", views.comments, name="comments"),
    path("edit_comment-<int:pk>/", views.edit_comment, name="edit_comment"),
    path("delete_comment-<int:pk>/", views.delete_comment, name="delete_comment"),
    path("like_comment-<int:pk>/", views.like_comment, name="like_comment"),

    # Posts
    path("posts/", views.posts, name="posts"),
    path("add_post/", views.add_post, name="add_post"),
    path("post-<int:post_id>/", views.post_detail, name="post_detail"),
    path("full_content-<int:post_id>/", views.full_content, name="full_content"),
    path("edit_post-<int:post_id>/", views.edit_post, name="edit_post"),
    path("delete_post-<int:post_id>/", views.delete_post, name="delete_post"),
    path("like_post-<int:post_id>/", views.like_post, name="like_post"),

    # Users
    path("users/", views.users, name="users"),
    path('user-<int:user_id>/', views.user_profile, name='user_profile'),
    path("user-<int:user_id>/posts/", views.user_posts, name="user_posts"),

    # Account Settings
    path("account-settings/", views.account_settings, name="account_settings"),
    path('change-email/', views.change_email, name='change_email'),
    path("delete_account/", views.delete_account, name="delete_account"),
]

