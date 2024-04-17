from django.urls import path

from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('login', views.login, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('dashboard', views.view_document, name='dashboard'),
    path('add_document', views.add_document, name='add_document'),
    path('received_online', views.received_online, name='received_online'),
    path('add_online_document', views.add_online_document, name='add_online_document'),
    path('display_code', views.display_code, name='display_code'),
    path('view_online_search', views.view_online_search, name='view_online_search'),
    path('reupload_online_document/<str:pk>/', views.reupload_online_document, name='reupload_online_document'),
    path('deny_online_document/<str:pk>/', views.deny_online_document, name='deny_online_document'),
    path('accept_document/<str:pk>/', views.accept_document, name='accept_document'),
    path('edit_document/<str:pk>/', views.edit_document, name='edit_document'),
    path('route_document/<str:pk>/', views.route_document, name='route_document'),
    path('document_history/<str:pk>/', views.document_history, name='document_history'),
    path('comment_document/<str:pk>/', views.comment_document, name='comment_document'),
    path('type_of_document', views.type_of_document, name='type_of_document'),
    path('type_of_action', views.type_of_action, name='type_of_action'),
    path('send_approved_document/<str:pk>/', views.send_approved_document, name='send_approved_document'),
    path('display_qrcode/<str:code>/', views.display_qrcode, name='display_qrcode'),
    path('for_release', views.for_release, name='for_release'),
    path('edit_type_of_action/<str:pk>/', views.edit_type_of_action, name='edit_type_of_action'),
    path('edit_type_of_document/<str:pk>/', views.edit_type_of_document, name='edit_type_of_document'),
    path('route_history', views.route_history, name='route_history'),
    path('route_history_code/<str:pk>', views.route_history_code, name='route_history_code'),
    path('report', views.report, name='report'),
    path('acted_menu', views.acted_menu, name='acted_menu'),
    path('copy_furnish', views.copy_furnish, name='copy_furnish'),
    path('my_docu_dashboard', views.my_docu_dashboard, name='my_docu_dashboard'),
    path('division_docs', views.division_docs, name='division_docs'),
    path('urgent_docs', views.urgent_docs, name='urgent_docs'),
    path('acted_release_docs', views.acted_release_docs, name='acted_release_docs'),
    path('due_docs', views.due_docs, name='due_docs'),
    path('to_due_docs', views.to_due_docs, name='to_due_docs'),
    path('all_due_docs', views.all_due_docs, name='all_due_docs'),
    path('outgoing', views.outgoing, name='outgoing'),
    path('add_outgoing', views.add_outgoing, name='add_outgoing'),
    path('detailed_copyfurnish/<str:pk>', views.detailed_copyfurnish, name='detailed_copyfurnish'),




]