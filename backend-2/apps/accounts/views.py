from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


User = get_user_model()


def user_payload(user):
	return {
		'id': user.pk,
		'email': user.email,
		'name': user.get_full_name() or user.email,
	}


@ensure_csrf_cookie
@api_view(['GET'])
@permission_classes([AllowAny])
def csrf_token(request):
	return Response({'csrfToken': get_token(request)})


@csrf_protect
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
	email = str(request.data.get('email', '')).strip().lower()
	name = str(request.data.get('name', '')).strip()
	password = request.data.get('password', '')

	from django.core.validators import validate_email
	try:
		validate_email(email)
	except ValidationError:
		return Response({'detail': 'Enter a valid email address.'}, status=status.HTTP_400_BAD_REQUEST)
	if len(email) > 150:
		return Response({'detail': 'Email addresses must be 150 characters or fewer.'}, status=status.HTTP_400_BAD_REQUEST)
	if not name:
		return Response({'detail': 'Enter your name.'}, status=status.HTTP_400_BAD_REQUEST)
	if User.objects.filter(email__iexact=email).exists() or User.objects.filter(username__iexact=email).exists():
		return Response({'detail': 'An account with this email already exists.'}, status=status.HTTP_409_CONFLICT)

	if not isinstance(password, str) or not password:
		return Response({'detail': 'Enter a password.'}, status=status.HTTP_400_BAD_REQUEST)

	candidate = User(username=email, email=email, first_name=name[:150])
	try:
		validate_password(password, candidate)
	except ValidationError as error:
		return Response({'detail': ' '.join(error.messages)}, status=status.HTTP_400_BAD_REQUEST)

	candidate.set_password(password)
	candidate.save()
	login(request, candidate)
	return Response({'user': user_payload(candidate)}, status=status.HTTP_201_CREATED)


@csrf_protect
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
	email = str(request.data.get('email', '')).strip().lower()
	password = request.data.get('password', '')
	if not email or not password:
		return Response({'detail': 'Enter your email and password.'}, status=status.HTTP_400_BAD_REQUEST)

	user_record = User.objects.filter(email__iexact=email).first()
	username = user_record.username if user_record else email
	user = authenticate(request, username=username, password=password)
	if user is None:
		return Response({'detail': 'Email or password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

	login(request, user)
	return Response({'user': user_payload(user)})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
	logout(request)
	return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def session_view(request):
	return Response({'user': user_payload(request.user)})
