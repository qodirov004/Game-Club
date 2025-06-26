from django.urls import path
from . import views

urlpatterns = [
    path('', views.game_list, name='game_list'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Games
    
    path('games/add/', views.add_game, name='add_game'),
    path('games/<int:pk>/edit/', views.edit_game, name='edit_game'),
    path('games/<int:pk>/delete/', views.delete_game, name='delete_game'),
    path('games/<int:pk>/start/', views.start_game, name='start_game'),
    path('stop_game/<int:game_pk>/', views.stop_game, name='stop_game'),
    
    # Game Sessions
    path('sessions/<int:pk>/', views.active_session, name='active_session'),
    path('sessions/<int:pk>/pause/', views.pause_session, name='pause_session'),
    path('sessions/<int:pk>/resume/', views.resume_session, name='resume_session'),
    path('sessions/<int:pk>/stop/', views.stop_session, name='stop_session'),
    
    # Completed Games
    path('completed-games/', views.completed_games, name='completed_games'),
    path('completed-games/<int:pk>/mark-as-paid/', views.mark_as_paid, name='mark_as_paid'),
    
    # Statistics
    path('statistics/', views.statistics, name='statistics'),
    
    # API
    path('api/sessions/<int:pk>/data/', views.get_session_data, name='get_session_data'),
]