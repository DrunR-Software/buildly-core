import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from social_django.utils import load_strategy, load_backend
from social_core.exceptions import MissingBackend, AuthException

from core.jwt_utils import CustomTokenObtainPairSerializer

logger = logging.getLogger(__name__)


class SocialConvertTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        backend_name = request.data.get('backend')
        token = request.data.get('token')

        if not backend_name or not token:
            return Response(
                {'error': 'backend and token are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        strategy = load_strategy(request)
        try:
            backend = load_backend(strategy, backend_name, redirect_uri=None)
        except MissingBackend:
            return Response(
                {'error': f'Unknown backend: {backend_name}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = backend.do_auth(token)
        except AuthException as e:
            logger.warning('Social auth failed for backend %s: %s', backend_name, e)
            return Response(
                {'error': 'Social authentication failed'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user or not user.is_active:
            return Response(
                {'error': 'Authentication failed or user is inactive'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = CustomTokenObtainPairSerializer.get_token(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })
