from django.db.models import F
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from prosper_investments.apps.terminology.models import Language, Translation


class TerminologyListView(APIView):
	permission_classes = (AllowAny,)

	# Avoids camel-case renderer, to preserve keys verbatim
	renderer_classes = (JSONRenderer,)

	def get(self, request):
		return Response({
			'availableLanguages': self._language_data(),
			'translations': self._translation_data(),
		})

	def _language_data(self):
		return Language.objects.filter(
			active=True
		).annotate(
			val=F('code'),
			label=F('name'),
		).values(
			'val', 'label',
		)

	def _translation_data(self):
		return Translation.objects.values_for_venue(venue=self.request.venue)
