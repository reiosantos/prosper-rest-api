from django.db import connections
from django.db.utils import OperationalError
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_503_SERVICE_UNAVAILABLE
from rest_framework.viewsets import ViewSet


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
