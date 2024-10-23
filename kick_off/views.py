import firebase_admin
from django.http import JsonResponse
from firebase_admin import auth
from firebase_admin.exceptions import FirebaseError
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import User, Points, Mission, Favorite, Video, Payment, Apply, Notification, Game, UserMission


# Firebase 전화번호 로그인 처리
@api_view(['POST'])
def phone_login(request):
    id_token = request.data.get('id_token')

    if not id_token:
        return Response({'error': 'Missing id_token'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Firebase ID 토큰 검증
        decoded_token = auth.verify_id_token(id_token)
    except Exception as e:
        return Response({'error': 'Invalid Firebase token'}, status=status.HTTP_400_BAD_REQUEST)

    # Firebase UID 및 전화번호 가져오기
    firebase_uid = decoded_token['uid']
    phone_number = decoded_token.get('phone_number', None)

    # 사용자가 이미 존재하는지 확인하고, 없으면 새로 생성
    user, created = User.objects.get_or_create(
        firebase_uid=firebase_uid,
        defaults={'phone_number': phone_number}
    )

    # 새로 생성된 사용자인지 여부에 따라 메시지 결정
    message = 'User created' if created else 'Login successful'

    return Response({
        'message': message,
        'user_id': user.user_id,
        'phone_number': user.phone_number
    })


# Firebase 토큰 검증 및 사용자 정보 저장
@api_view(['POST'])
def verify_firebase_token(request):
    id_token = request.data.get('id_token')

    try:
        # Firebase ID 토큰 검증
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        phone_number = decoded_token.get('phone_number', None)

        # MySQL에 사용자 정보 저장 또는 업데이트
        user, created = User.objects.get_or_create(firebase_uid=uid)
        if created:
            user.phone_number = phone_number
            user.save()

        return JsonResponse({"message": "User authenticated", "user_id": user.id})

    except FirebaseError as e:
        return JsonResponse({"error": str(e)}, status=400)


# 전화번호 인증 코드 전송
@api_view(['POST'])
def send_verification_code_view(request):
    phone_number = request.data.get('phone_number')

    if not phone_number:
        return Response({'error': 'Missing phone number'}, status=status.HTTP_400_BAD_REQUEST)

    # 인증 코드 생성 및 전송 로직 (예: Twilio 또는 Firebase SMS API 사용)
    verification_code = "123456"  # 실제 구현에서는 무작위 생성
    # 인증 코드 전송 로직 필요

    return Response({'message': 'Verification code sent successfully'})


# 전화번호 인증 코드 검증
@api_view(['POST'])
def verify_code_view(request):
    phone_number = request.data.get('phone_number')
    verification_code = request.data.get('verification_code')

    if not phone_number or not verification_code:
        return Response({'error': 'Missing phone number or verification code'}, status=status.HTTP_400_BAD_REQUEST)

    # 인증 코드 검증 로직
    if verification_code == "123456":  # 실제 구현에서는 검증 과정 추가
        return Response({'message': 'Verification successful'})

    return Response({'error': 'Invalid verification code'}, status=status.HTTP_400_BAD_REQUEST)


# 사용자 조회
@api_view(['GET'])
def get_user_profile(request, user_id):
    user = get_object_or_404(User, user_id=user_id)
    data = {
        'name': user.name,
        'email': user.email,
        'phone_number': user.phone_number,
        'points': user.points,
        'profile_picture': user.profile_picture,
        'level': user.level.id if user.level else None,
        'registration_date': user.registration_date
    }
    return Response(data)


# 사용자 프로필 업데이트
@api_view(['POST'])
def update_user_profile(request, user_id):
    user = get_object_or_404(User, user_id=user_id)

    phone_number = request.data.get('phone_number')
    profile_picture = request.data.get('profile_picture')

    if phone_number:
        user.phone_number = phone_number
    if profile_picture:
        user.profile_picture = profile_picture

    user.save()
    return Response({'message': 'Profile updated successfully'})


# 사용자 삭제
@api_view(['DELETE'])
def delete_user(request, user_id):
    user = get_object_or_404(User, user_id=user_id)
    user.delete()
    return Response({'message': f'User {user.name} deleted successfully'})


# 게임 정보 조회
@api_view(['GET'])
@permission_classes([AllowAny])  # 인증 필요 없는 뷰로 설정
def get_game_info(request, game_id):
    game = get_object_or_404(Game, game_id=game_id)
    data = {
        'game_name': game.game_name,
        'game_date': game.game_date,
        'game_time': game.game_time,
        'location': game.location,
        'status': game.status,
    }
    return Response(data)


# 특정 레벨 사용자 게임 참여
@api_view(['POST'])
def join_game(request, game_id):
    game = get_object_or_404(Game, game_id=game_id)
    user = request.user  # 인증된 사용자를 가져옵니다.

    # 사용자의 레벨이 게임에 맞는지 확인
    if user.level != game.level:
        return Response({'error': '이 게임은 사용자의 레벨에 맞지 않습니다.'}, status=status.HTTP_403_FORBIDDEN)

    # 게임 참여 로직 실행
    game.participants.add(user)
    return Response({'message': '게임에 성공적으로 참여했습니다.'})


# 포인트 조회
@api_view(['GET'])
def get_user_points(request, user_id):
    points = Points.objects.filter(user__user_id=user_id)
    if points.exists():
        data = [{'points_amount': p.points_amount, 'event_date': p.event_date, 'total_points': p.total_points} for p in
                points]
        return Response(data)
    return Response({'error': 'Points not found'}, status=status.HTTP_404_NOT_FOUND)


# 포인트 추가
@api_view(['POST'])
def add_points(request, user_id):
    user = get_object_or_404(User, user_id=user_id)
    points_to_add = request.data.get('points')

    if not points_to_add or not isinstance(points_to_add, int):
        return Response({'error': 'Invalid points value'}, status=status.HTTP_400_BAD_REQUEST)

    user.points += points_to_add
    user.save()

    return Response({'message': f'{points_to_add} points added to user {user.name}'})


# 미션 조회
@api_view(['GET'])
@permission_classes([AllowAny])  # 인증 필요 없는 뷰로 설정
def get_missions(request):
    missions = Mission.objects.all()
    data = [{
        'mission_id': m.mission_id,
        'mission_name': m.mission_name,
        'mission_content': m.mission_content,
        'points': m.points,
        'video_url': m.video_url,
        'mission_type': m.mission_type
    } for m in missions]
    return Response(data)


# 특정 미션 조회
@api_view(['GET'])
@permission_classes([AllowAny])  # 인증 필요 없는 뷰로 설정
def get_mission_detail(request, mission_id):
    mission = get_object_or_404(Mission, mission_id=mission_id)
    data = {
        'mission_id': mission.mission_id,
        'mission_name': mission.mission_name,
        'mission_content': mission.mission_content,
        'points': mission.points,
        'video_url': mission.video_url,
        'mission_type': mission.mission_type,
    }
    return Response(data)


# 사용자 미션 완료 상태 조회
@api_view(['GET'])
def get_user_mission_status(request, user_id):
    user_missions = UserMission.objects.filter(user__user_id=user_id)
    all_missions = Mission.objects.all()

    data = [{
        'mission_id': mission.mission_id,
        'mission_name': mission.mission_name,
        'mission_content': mission.mission_content,
        'points': mission.points,
        'video_url': mission.video_url,
        'mission_type': mission.mission_type,
        'completed': user_missions.filter(mission=mission).exists()  # 미션 완료 여부 확인
    } for mission in all_missions]

    return Response(data)


# 관심 게임 조회
@api_view(['GET'])
def get_favorite_games(request, user_id):
    favorites = Favorite.objects.filter(user__user_id=user_id)
    if favorites.exists():
        data = [{'game': f.game.game_name, 'liked': f.liked} for f in favorites]
        return Response(data)
    return Response({'error': 'Favorites not found'}, status=status.HTTP_404_NOT_FOUND)


# 관심 게임 추가
@api_view(['POST'])
def add_favorite_game(request, user_id, game_id):
    user = get_object_or_404(User, user_id=user_id)
    game = get_object_or_404(Game, game_id=game_id)

    # 관심 게임에 추가
    favorite, created = Favorite.objects.get_or_create(user=user, game=game)
    if created:
        return Response({'message': 'Game added to favorites'}, status=status.HTTP_201_CREATED)

    return Response({'error': 'Game already in favorites'}, status=status.HTTP_400_BAD_REQUEST)


# 관심 게임 제거
@api_view(['POST'])
def remove_favorite_game(request, user_id, game_id):
    user = get_object_or_404(User, user_id=user_id)
    game = get_object_or_404(Game, game_id=game_id)

    favorite = Favorite.objects.filter(user=user, game=game).first()
    if favorite:
        favorite.delete()
        return Response({'message': 'Game removed from favorites'})

    return Response({'error': 'Favorite not found'}, status=status.HTTP_404_NOT_FOUND)


# 특정 게임의 영상 조회
@api_view(['GET'])
def get_game_videos(request, game_id):
    videos = Video.objects.filter(game__game_id=game_id)
    if videos.exists():
        data = [{'video_url': v.video_url, 'upload_date': v.upload_date} for v in videos]
        return Response(data)
    return Response({'error': 'Videos not found'}, status=status.HTTP_404_NOT_FOUND)


# 영상 조회
@api_view(['GET'])
def get_user_videos(request, user_id):
    videos = Video.objects.filter(game__game_id=user_id)
    if videos.exists():
        data = [{'video_url': v.video_url, 'upload_date': v.upload_date} for v in videos]
        return Response(data)
    return Response({'error': 'Videos not found'}, status=status.HTTP_404_NOT_FOUND)


# 결제 내역 조회
@api_view(['GET'])
def get_user_payments(request, user_id):
    payments = Payment.objects.filter(user__user_id=user_id)
    if payments.exists():
        data = [{'amount': p.amount, 'status': p.payment_status, 'date': p.payment_date} for p in payments]
        return Response(data)
    return Response({'error': 'Payments not found'}, status=status.HTTP_404_NOT_FOUND)


# 결제 처리
@api_view(['POST'])
def make_payment(request, user_id):
    user = get_object_or_404(User, user_id=user_id)
    amount = request.data.get('amount')

    if not amount or float(amount) <= 0:
        return Response({'error': 'Invalid payment amount'}, status=status.HTTP_400_BAD_REQUEST)

    payment = Payment.objects.create(user=user, amount=amount, payment_status='Pending')
    payment.save()

    return Response({'message': 'Payment initiated', 'payment_id': payment.payment_id})


# 신청 내역 조회
@api_view(['GET'])
def get_user_applies(request, user_id):
    applies = Apply.objects.filter(user__user_id=user_id)
    if applies.exists():
        data = [{'game': a.game.game_name, 'status': a.apply_status, 'apply_date': a.apply_date} for a in applies]
        return Response(data)
    return Response({'error': 'Applies not found'}, status=status.HTTP_404_NOT_FOUND)


# 게임 신청
@api_view(['POST'])
def apply_for_game(request, user_id, game_id):
    user = get_object_or_404(User, user_id=user_id)
    game = get_object_or_404(Game, game_id=game_id)

    # 이미 신청한 경우 예외 처리
    if Apply.objects.filter(user=user, game=game).exists():
        return Response({'error': 'Already applied for this game'}, status=status.HTTP_400_BAD_REQUEST)

    apply = Apply.objects.create(user=user, game=game, apply_status='Pending')
    apply.save()

    return Response({'message': 'Game application successful'}, status=status.HTTP_201_CREATED)


# 게임 신청 취소
@api_view(['POST'])
def cancel_application(request, user_id, game_id):
    user = get_object_or_404(User, user_id=user_id)
    game = get_object_or_404(Game, game_id=game_id)
    application = Apply.objects.filter(user=user, game=game).first()

    if not application:
        return Response({'error': 'No application found for this game'}, status=status.HTTP_404_NOT_FOUND)

    application.delete()
    return Response({'message': 'Application cancelled successfully'}, status=status.HTTP_200_OK)


# 알림 조회
@api_view(['GET'])
def get_user_notifications(request, user_id):
    notifications = Notification.objects.filter(user__user_id=user_id)
    if notifications.exists():
        data = [{'content': n.content, 'notification_type': n.notification_type, 'creation_date': n.creation_date} for n
                in notifications]
        return Response(data)
    return Response({'error': 'Notifications not found'}, status=status.HTTP_404_NOT_FOUND)


# 알림 읽음 처리
@api_view(['POST'])
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, notification_id=notification_id)
    # 알림 읽음 처리 로직
    notification.read = True
    notification.save()

    return Response({'message': 'Notification marked as read'}, status=status.HTTP_200_OK)