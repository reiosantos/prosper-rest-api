from django.apps import apps
from rest_framework import exceptions, HTTP_HEADER_ENCODING
from rest_framework.authentication import get_authorization_header, BaseAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication


class JSONWebTokenAuthenticationPost(JSONWebTokenAuthentication):
	"""
	Look for JWT sent in the POST body, if it's missing from the header.
	"""

	def authenticate(self, request):
		if not get_authorization_header(request):
			jwt = request.POST.get('jwt')
			if jwt:
				request.META['HTTP_AUTHORIZATION'] = "JWT %s" % jwt
		return super(JSONWebTokenAuthenticationPost, self).authenticate(request)


class ApiKeyAuthentication(BaseAuthentication):
	"""
	Simple api key based authentication.

	Clients should authenticate by passing the api key in the "X-API-Key"
	HTTP header".  For example:

		X-API-Key: 401f7ac837da42b97f613d789819ff93537bee6a
	"""

	# model = apps.get_model(app_label='prosper_investments.apps.user', model_name='ApiKey')

	"""
	A custom token model may be used, but must have the following properties.

	* key -- The string identifying the token
	* user -- The user to which the token belongs
	"""

	def authenticate(self, request):
		auth = self.get_api_key_header(request).split()

		if not auth:
			return None

		return self.authenticate_credentials(auth[0])

	def authenticate_credentials(self, key):
		self.model = apps.get_model(app_label='prosper_investments.apps.user', model_name='ApiKey')

		try:
			api_key = self.model.objects.select_related('user').get(key=key)
		except self.model.DoesNotExist:
			raise exceptions.AuthenticationFailed({'error': 'Invalid api_key.'})

		if not api_key.user.is_active:
			raise exceptions.AuthenticationFailed({'error': 'User inactive or deleted.'})

		return api_key.user, api_key

	@staticmethod
	def get_api_key_header(request):
		"""
		Return request's 'X-API-Key:' header, as a bytestring.

		Hide some test client ickyness where the header can be unicode.
		"""
		auth = request.META.get('HTTP_X_API_KEY', '')
		if isinstance(auth, type('')):
			# Work around django test client oddness
			auth = auth.encode(HTTP_HEADER_ENCODING)
		return auth
