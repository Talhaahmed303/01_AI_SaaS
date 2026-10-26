from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .serializers import UserRegisterSerializer, UserSerializer, CustomTokenObtainPairSerializer
from usage.models import UserQuota

User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'status': 'success',
            'message': 'User registered successfully with default workspace provisioned.',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

class UpdateTierView(APIView):
    """Utility endpoint to simulate tier upgrades (FREE -> PRO -> ENTERPRISE) for demo & testing."""
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        tier = request.data.get('tier', 'PRO').upper()
        if tier not in ['FREE', 'PRO', 'ENTERPRISE']:
            return Response({'error': 'Invalid tier. Choose FREE, PRO, or ENTERPRISE.'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        user.tier = tier
        user.save()

        quota, _ = UserQuota.objects.get_or_create(user=user)
        quota.tier = tier
        if tier == 'FREE':
            quota.daily_query_limit = 30
            quota.daily_token_limit = 50000
        elif tier == 'PRO':
            quota.daily_query_limit = 500
            quota.daily_token_limit = 500000
        elif tier == 'ENTERPRISE':
            quota.daily_query_limit = 10000
            quota.daily_token_limit = 5000000
        quota.save()

        return Response({
            'status': 'success',
            'message': f'Subscription tier upgraded to {tier}',
            'user': UserSerializer(user).data
        })
