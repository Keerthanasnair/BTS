"""
URL configuration for bts project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from btsapp.views import *

urlpatterns = [
    path('',login_page),
    path('login_page/',login_page,name='login_page'),
    path('login/',login,name="login"),
    path('register/',register,name="register"),
    path('logout/',logout,name="logout"),
    path('admin_home/',admin_home,name="admin_home"),
    path('developer_home/',developer_home,name="developer_home"),
    path('tester_home/',tester_home,name="tester_home"),
    path('check_tasks/',check_tasks,name="check_tasks"),
    path('task_assign/',task_assign,name='task_assign'),
    path('assign_website/',assign_website,name='assign_website'),
    path('users_list/',users_list,name='users_list'),
    path('users_list/edit_user/',edit_user,name='edit_user'),
    path('users_list/delete_user/',delete_user,name='delete_user'),
    path('dashboard_summary/',dashboard_summary,name='dashboard_summary'),
    path('notifications/',notifications,name='notifications'),
    path('mark_as_read/',mark_as_read,name='mark_as_read'),
    path('upload_page/',upload_page,name='upload_page'),
    path('upload_script/',upload_script,name='upload_script'),
    path('developer_submit_website_page/',developer_submit_website_page,name='developer_submit_website_page'),
    path('developer_submit_webiste/',developer_submit_website,name='developer_submit_website'),
    path('developer_view_status/',developer_view_status,name='developer_view_status'),
    path('tester_review_script/',tester_review_script,name='tester_review_script'),
    path('check_tasks/assigned_tasks/',assigned_tasks,name='assigned_tasks'),
    path('check_tasks/assign_website/',assign_website,name='assign_website'),
    path('tasks_page/',tasks_page,name='tasks_page'),
    path('report_page/',report_page,name='report_page'),
    path('tester_review_script/',tester_review_script,name='tester_review_script'),
    path('tasks_page/test_script/',test_script,name='test_script'),
    path('tasks_page/accept_task/',accept_task,name='accept_task'),
    path('tasks_page/accept_website_task/',accept_website_task,name='accept_website_task'),
    
    path('tasks_page/review_website/',review_website,name='review_website'),
    path('tasks_page/review_website_page/',review_website_page,name='review_website_page'),
    
    path('tasks_page/review_website_page/submit_website_report/',submit_website_report,name='submit_website_report'),
    
    path('tester_review_script/submit_report/',submit_report,name='submit_report'),    
    path('task_assign/summarize/',summarize,name='summarize'),
    path('completed_reports/',completed_reports,name='completed_reports'),
    path('chat/', chat, name='chat'),
    path('chat_page/', chat_page, name='chat_page'),  
    path('total_task/', total_task, name='total_task'),    
    path('pending_task/', pending_task, name='pending_task'),    
    path('completed_task/', completed_task, name='completed_task'),    
    path('dev_completed/', dev_completed, name='dev_completed'),    
    path('dev_pending/', dev_pending, name='dev_pending'),    
    path('dev_total/', dev_total, name='dev_total'),  
    path('dev_pend_review/', dev_pend_review, name='dev_pend_review'), 
    path('tester_total/', tester_total, name='tester_total'),  
    path('tester_progress/', tester_progress, name='tester_progress'),  
    path('dev_summarize/',dev_summarize,name='summarize'),


]
