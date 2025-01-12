
from django.contrib import admin
from django.urls import path
from finance_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.index),
    path('user_reg/',views.user_reg),
    path('exp_reg/',views.exp_reg),
    path('login/',views.login),
    path('adminhome/',views.adminhome),
    path('userhome/',views.userhome),
    path('experthome/',views.experthome),
    path('add_expense/',views.add_expense),
    path('remove_expense/',views.remove_expense,name="remove_expense"),
    path('edit_expense/',views.edit_expense,name="edit_expense"),
    path('set_budget/',views.set_budget,name="set_budget"),
    path('set_saving_goal/',views.set_saving_goal,name="set_saving_goal"),
    path('update_goal/',views.update_goal,name="update_goal"),
    path('user_update_profile/',views.user_update_profile,name="user_update_profile"),
    path('admin_user_approve/',views.admin_user_approve,name="admin_user_approve"),
     path('view_user_details/<int:user_id>/', views.view_user_details, name='view_user_details'),
     path('admin_expert_approve/',views.admin_expert_approve,name="admin_expert_approve"),
     path('expert_user_view/',views.expert_user_view,name="expert_user_view"),
     path('expert_chat/',views.expert_chat,name="expert_chat"),
     path('user_chat/',views.user_chat,name="user_chat"),
     path('view_experts',views.view_experts,name="view_experts"),
]
