from django.urls import path, include
from .views import (
    send_verification_code_view, verify_code_view,
    get_user_profile, update_user_profile, delete_user,
    get_game_info, join_game,
    get_user_points, add_points,
    get_missions, get_mission_detail, get_user_mission_status,
    get_favorite_games, add_favorite_game, remove_favorite_game,
    get_user_videos, get_game_videos,
    get_user_payments, make_payment,
    get_user_applies, apply_for_game, cancel_application,
    get_user_notifications, mark_notification_read
)

urlpatterns = [
    # 전화번호 로그인 API
    path('auth/send-code/', send_verification_code_view, name='send_code'),
    path('auth/verify-code/', verify_code_view, name='verify_code'),

    # 사용자 관련 API
    path('users/<int:user_id>/', get_user_profile, name='get_user_profile'),
    path('users/<int:user_id>/update/', update_user_profile, name='update_user_profile'),
    path('users/<int:user_id>/delete/', delete_user, name='delete_user'),

    # 게임 관련 API
    path('games/<int:game_id>/', get_game_info, name='get_game_info'),
    path('games/<int:game_id>/join/', join_game, name='join_game'),

    # 포인트 관련 API
    path('points/<int:user_id>/', get_user_points, name='get_user_points'),
    path('points/<int:user_id>/add/', add_points, name='add_points'),

    # 미션 관련 API
    path('missions/', get_missions, name='get_missions'),
    path('missions/<int:mission_id>/', get_mission_detail, name='get_mission_detail'),
    path('missions/user/<int:user_id>/', get_user_mission_status, name='get_user_mission_status'),

    # 관심 게임 관련 API
    path('favorites/<int:user_id>/', get_favorite_games, name='get_favorite_games'),
    path('favorites/<int:user_id>/add/<int:game_id>/', add_favorite_game, name='add_favorite_game'),
    path('favorites/<int:user_id>/remove/<int:game_id>/', remove_favorite_game, name='remove_favorite_game'),

    # 영상 관련 API
    path('videos/<int:user_id>/', get_user_videos, name='get_user_videos'),
    path('videos/game/<int:game_id>/', get_game_videos, name='get_game_videos'),

    # 결제 관련 API
    path('payments/<int:user_id>/', get_user_payments, name='get_user_payments'),
    path('payments/<int:user_id>/make/', make_payment, name='make_payment'),

    # 신청 내역 관련 API
    path('applies/<int:user_id>/', get_user_applies, name='get_user_applies'),
    path('applies/<int:user_id>/apply/<int:game_id>/', apply_for_game, name='apply_for_game'),
    path('applies/<int:user_id>/cancel/<int:game_id>/', cancel_application, name='cancel_application'),

    # 알림 관련 API
    path('notifications/<int:user_id>/', get_user_notifications, name='get_user_notifications'),
    path('notifications/<int:notification_id>/read/', mark_notification_read, name='mark_notification_read'),
]
