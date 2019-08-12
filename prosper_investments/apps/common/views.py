from django.db import connections
from django.db.utils import OperationalError
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_503_SERVICE_UNAVAILABLE, HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ViewSet

from prosper_investments.apps.user.models import ApiKey


class ApiKeyVerify(ViewSet):
	permission_classes = []

	def post(self, request):
		key = request.data.get('apikey', None)
		if key is None:
			return Response(status=HTTP_400_BAD_REQUEST)

		try:
			apikey = ApiKey.objects.get(key=request.data['apikey'])
			if apikey:
				user_data = {
					'username': apikey.user.email,
					'userId': apikey.user.pk,
					'email': apikey.user.email,
					'venueId': apikey.user.venues.first().url_component
				}
				return Response({'userData': user_data}, status=HTTP_200_OK)
		except ApiKey.DoesNotExist:
			return Response(status=HTTP_400_BAD_REQUEST)

		return Response(status=HTTP_200_OK)


class HealthCheckView(ViewSet):
	permission_classes = []

	# noinspection PyBroadException
	def get(self, request):
		error_response = Response({'status': False}, status=HTTP_503_SERVICE_UNAVAILABLE)

		try:
			conn = connections['default']
			conn.cursor()
		except OperationalError:
			return error_response

		return Response({'status': True}, status=HTTP_200_OK)
