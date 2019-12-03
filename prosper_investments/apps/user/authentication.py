from rest_framework.authentication import get_authorization_header
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
