from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('create_profile/', views.create_or_edit_profile, name='create_profile'),
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path("update_profile/", views.update_profile, name="edit_profile"),
    
    path("blog/", views.blog, name="blogs"),
    path('blog/<uuid:blog_id>/increment-view/', views.increment_blog_view, name='increment_blog_view'),
     
    path("creaate_blog/", views.create_blog, name="create_blog"),
    path('edit/<slug:slug>/', views.edit_blog, name='edit_blog'),
    path('delete/<slug:slug>/', views.delete_blog, name='delete_blog'),
    path('tags/suggestions/', views.tag_suggestions, name='tag_suggestions'),
    path('categories/suggestions/', views.category_suggestions, name='category_suggestions'),

    path('user/<str:username>/', views.view_user_profile, name='view_user_profile'),

    path('user_blog/', views.my_blogs, name='user_blog'),
    path('like/<uuid:blog_id>/', views.toggle_like, name='toggle_like'),
    path('<uuid:blog_id>/comments/', views.load_comments, name='load_comments'),
    path('comment/<uuid:blog_id>/add/', views.add_comment, name='add_comment'),
    path('trending_blogs/', views.trending, name='trending'),
    path('settings/', views.setting, name='setting'),
    path('settings/update/', views.update_settings, name='update_settings'),
    path('settings/change-password/', views.change_password, name='change_password'),
    path('try-another-way/', views.try_another_way, name='try_another_way'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('email-settings/', views.email_settings, name='email_settings'),
    path('email-settings/add/', views.add_email, name='add_email'),
    path('email-settings/delete/<int:email_id>/', views.delete_email, name='delete_email'),
    path('email-settings/set-primary/<int:email_id>/', views.set_primary_email, name='set_primary_email'),

    path('email-settings/send-otp/', views.send_email_otp, name='send_email_otp'),            # POST to send OTP for a new email
    path('email-settings/send-otp/<int:email_id>/', views.send_email_otp, name='resend_email_otp'),  # resend
    path('email-settings/verify/', views.email_verify_page, name='email_verify'),
    path("email/resend/<str:email>/", views.resend_verification, name="resend_verification"),
    path('email-settings/verify/confirm/', views.verify_email_otp, name='verify_email_otp'),
    path('logout/', views.logout_view, name='logout'), 
    
    
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('follow/toggle/<str:username>/', views.toggle_follow_ajax, name='toggle_follow_ajax'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),
    path('follow/send/<str:username>/', views.send_follow_request, name='send_follow_request'),
    path('follow/approve/<str:follower_username>/', views.approve_follow_request, name='approve_follow_request'),
    path('follow/reject/<str:follower_username>/', views.reject_follow_request, name='reject_follow_request'),
    path('search-users/', views.search_users, name='search_users'),
    path('notifications/', views.notification_panel, name='notifications'),
    path('notifications/mark_all_read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/clear_all/', views.clear_all_notifications, name='clear_all_notifications'),
    path('notifications/follow_request/<int:notif_id>/<str:action>/', views.handle_follow_request, name='handle_follow_request'),

    path('ajax/follow-counts/<str:username>/', views.get_follow_counts, name='ajax_follow_counts'),
    path('ajax/follow-counts/', views.get_follow_counts, name='ajax_follow_counts_current'),
    path('delete_account/', views.delete_account, name='delete_account'),
]