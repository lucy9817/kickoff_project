import random

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


# 레벨 테이블
class Level(models.Model):
    LEVEL_CHOICES = [
        ('Novice', '뉴비'),
        ('Rookie', '루키'),
        ('Professional', '프로페셜'),
        ('Elite', '엘리트'),
        ('Maestro', '마에스트로'),
        ('Legend', '레전드'),
    ]

    COLOR_CHOICES = [
        ('#FF0000', 'Red'),  # 뉴비
        ('#000080', 'Navy'),  # 루키
        ('#FB36FF', 'Pink'),  # 프로페셔널
        ('#9F09AC', 'Purple'),  # 엘리트
        ('#000000', 'Black'),  # 마에스트로
        ('#D1A722', 'Gold'), #레전드
    ]

    name = models.CharField(choices=LEVEL_CHOICES, max_length=20)
    color = models.CharField(choices=COLOR_CHOICES, max_length=7)
    whistle = models.IntegerField(validators=[
            MinValueValidator(0),   # 최소 0
            MaxValueValidator(3)    # 최대 3
        ])  # 호루라기 단계
    level_number = models.IntegerField(validators=[
            MinValueValidator(0),   # 최소 0
            MaxValueValidator(3)    # 최대 3
        ])  # 레벨 번호

    def clean(self):
        super().clean()
        # 레전드 레벨일 경우 whistle이 1로 제한
        if self.name == 'Legend' and self.whistle != 1:
            raise ValidationError({'whistle': 'Legend level can only have 1 whistle.'})

    def __str__(self):
        return f'{self.name} - Level {self.level_number}'


# 사용자 테이블 (User)
class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)  # 이름 필드를 최대 20자로 제한
    email = models.EmailField(blank=True, null=True)  # 이메일은 선택 사항
    level = models.ForeignKey(Level, on_delete=models.CASCADE)  # 필수로 설정
    phone_number = models.CharField(max_length=15, unique=True)   # 필수 필드로 설정
    firebase_uid = models.CharField(max_length=255, unique=True, blank=True, null=True)  # Firebase 사용자 고유 ID
    points = models.IntegerField(default=0)
    registration_date = models.DateTimeField(auto_now_add=True)
    profile_picture = models.URLField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name


# 경기 테이블 (Game)
class Game(models.Model):
    game_id = models.AutoField(primary_key=True)
    game_name = models.CharField(max_length=100)
    game_date = models.DateField()
    game_time = models.TimeField()
    location = models.CharField(max_length=255)
    max_participants = models.IntegerField()

    # 참가자 관리: User 모델과 Many-to-Many 관계 설정
    participants = models.ManyToManyField(User, blank=True)

    REGION_CHOICES = [
        ('seoul', '서울'),
        ('gyeonggi', '경기'),
    ]
    region = models.CharField(max_length=20, choices=REGION_CHOICES)

    GENDER_CHOICES = [
        ('male', '남자'),
        ('female', '여자'),
        ('mixed', '혼성'),
    ]
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)

    # 경기 참가를 위한 최소 사용자 레벨을 의미
    level = models.ForeignKey(Level, on_delete=models.PROTECT)  # 사용자 레벨을 필수로 설정

    promotion_match = models.BooleanField(default=False)

    STATUS_CHOICES = [
        ('upcoming', '신청하기'),
        ('in-progress', '진행중'),
        ('finished', '마감'),
        ('cancelled', '취소하기'),
    ]
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='upcoming')  # 기본값 설정

    def clean(self):
        # 참가자 수가 max_participants를 초과하지 않는지 확인
        if self.participants.count() > self.max_participants:
            raise ValidationError(f'참가자는 최대 {self.max_participants}명까지 가능합니다.')

        # 참가자의 레벨이 경기에 필요한 최소 레벨을 충족하는지 확인
        for participant in self.participants.all():
            if participant.level.level_number < self.level.level_number:
                raise ValidationError(f'{participant.name}님의 레벨이 경기에 필요한 최소 레벨보다 낮습니다.')

    def save(self, *args, **kwargs):
        # 참가자 수가 가득 찼을 때 상태를 자동으로 'finished'로 변경
        if self.participants.count() >= self.max_participants:
            self.status = 'finished'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.game_name} - {self.region} - {self.status}"


# 포인트 내역 테이블 (Points)
class Points(models.Model):
    points_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_points')  # related_name 추가
    POINTS_LOG_CHOICES = [
        ('earned', 'Earned'),
        ('deducted', 'Deducted'),
    ]
    points_log = models.CharField(max_length=10, choices=POINTS_LOG_CHOICES)
    total_points = models.IntegerField()
    event_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Points for {self.user.name}"


# 미션 테이블 (Mission)

class Mission(models.Model):
    MISSION_TYPE_CHOICES = [
        ('individual', '개인 미션'),
        ('team', '팀 미션'),
    ]

    mission_id = models.AutoField(primary_key=True)
    mission_name = models.CharField(max_length=100)  # 비NULL 필드
    mission_content = models.TextField()              # 미션 내용
    video_url = models.URLField(max_length=255, blank=True, null=True)  # 미션 예시 이미지 URL
    points = models.IntegerField()                    # 획득할 수 있는 포인트
    mission_type = models.CharField(max_length=10, choices=MISSION_TYPE_CHOICES)  # 미션 유형 추가
    completion_status = models.BooleanField(default=False)    # 완료 상태
    upload_date = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Mission {self.mission_id}: {self.mission_name}"

class UserMission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)  # 미션 완료 여부
    completion_date = models.DateTimeField(auto_now_add=True)  # 완료한 날짜


# 관심 매치 테이블 (Favorite)
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    liked = models.BooleanField(default=True)

    class Meta:
        unique_together = (('user', 'game'),)  # 복합 기본키 설정

    def __str__(self):
        return f"Favorite for {self.user.name}"


# 영상 내역 테이블 (Video)
class Video(models.Model):
    video_id = models.AutoField(primary_key=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    video_url = models.URLField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Video {self.video_id} for {self.game.game_name}"


# 결제 테이블 (Payment)
class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
        ('Refunded', 'Refunded'),
    ]
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES)
    PAYMENT_METHOD_CHOICES = [
        ('Bank Transfer', 'Bank Transfer'),
    ]
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.payment_id} for {self.user.name}"


# 신청 내역 테이블 (Apply)
class Apply(models.Model):
    apply_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    apply_date = models.DateTimeField(auto_now_add=True)
    APPLY_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
        ('Cancelled', 'Cancelled'),
    ]
    apply_status = models.CharField(max_length=10, choices=APPLY_STATUS_CHOICES)

    def __str__(self):
        return f"Apply {self.apply_id} for {self.user.name}"


# 알림 테이블 (Notification)
class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    NOTIFICATION_TYPE_CHOICES = [
        ('game_notification', 'Game Notification'),
        ('system_notification', 'System Notification'),
        ('other', 'Other'),
    ]
    is_read = models.BooleanField(default=False)  # 알림 읽음 여부 추가
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    creation_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification {self.notification_id} for {self.user.name}"
