"""
Email Views
"""
import logging
from datetime import date

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from prosper_investments.apps.email.utils import CardErrorEmail
from prosper_investments.apps.venue.models import VenueSetting, VenueSettingValue

logger = logging.getLogger(__name__)


class CardErrorNotification(APIView):
	permission_classes = (AllowAny,)

	def post(self, request):
		try:
			setting = VenueSetting.objects.get(var_define='VENUE_ADMIN_EMAIL')
		except VenueSetting.DoesNotExist:
			raise VenueSetting.DoesNotExist("Venue Setting 'VENUE_ADMIN_EMAIL' is not set.")

		try:
			venue_admin_email = VenueSettingValue.objects.get(
				setting=setting, venue=self.request.venue).value
		except VenueSettingValue.DoesNotExist:
			venue_admin_email = ''

		context = {
			'user_name': request.user.full_name,
			'user_email': request.user.email,
			'venue_admin_email': venue_admin_email,
			'request': request,
			'date': date.today().strftime('%B %d, %Y')
		}
		email = CardErrorEmail(model_instance=context, context=context)

		try:
			email.send()
		except Exception as e:
			logger.error("Error sending email: %s" % e)

		return Response(data={"message": "success"}, status=200)
