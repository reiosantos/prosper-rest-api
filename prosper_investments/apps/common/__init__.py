import logging
import sys
import traceback

from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler as default_exception_handler

logger = logging.getLogger('prosper_investments')


def exception_handler(exc, context):
	exc_type, exc_value, exc_traceback = sys.exc_info()
	call_stack = '\n'.join(traceback.format_tb(exc_traceback))
	error_list = [
		'\n\nRequest URL: %s' % str(context['request']._request),
		'Error type: %s' % exc_type,
		'Error value: %s' % exc_value,
		'Payload: %s' % str(context['request'].query_params),
		'Message: %s' % str(exc), '----Call stack----\n %s' % call_stack,
		'------Locals------\n %s' % str(context['request']._request.__dict__)
	]
	error_msg = '\n'.join(error_list)

	# Too many NotAuthenticated exceptions, so we won't log them for now, see PD-678
	if exc_type != NotAuthenticated and exc_type != PermissionDenied and exc_type != ValidationError:
		logger.error(error_msg)
	else:
		logger.info(error_msg)

	original_response = default_exception_handler(exc, context)

	if original_response is not None:
		return original_response
	return Response(
		status=status.HTTP_500_INTERNAL_SERVER_ERROR, data=str(exc), content_type='application/json')
