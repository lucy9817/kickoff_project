from django.contrib import admin
from .models import Mission, User, Game, Level, Points, Favorite, Video, Payment, Apply, Notification, UserMission

# 사용자 관리 - 검색, 필터 등 추가
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'level', 'points', 'registration_date')
    search_fields = ('name', 'email')
    list_filter = ('level', 'registration_date')

# 미션 관리 - 검색, 필터 등 추가
@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ('mission_name', 'points', 'mission_type', 'completion_status', 'upload_date')
    search_fields = ('mission_name', 'mission_content')
    list_filter = ('mission_type', 'completion_status')

# 게임 관리
@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('game_name', 'game_date', 'location', 'status')
    search_fields = ('game_name',)
    list_filter = ('status', 'game_date')

# 다른 모델들 기본 등록
admin.site.register(Level)
admin.site.register(Points)
admin.site.register(Favorite)
admin.site.register(Video)
admin.site.register(Payment)
admin.site.register(Apply)
admin.site.register(Notification)
admin.site.register(UserMission)
