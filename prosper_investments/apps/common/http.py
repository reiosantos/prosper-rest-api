import logging

import requests
from requests.sessions import Session
from rest_framework import status
from rest_framework.response import Response

logger = logging.getLogger(__name__)


def send_req(method, url, params=None, headers=None, json=None):
	params = {} if params is None else params
	headers = [] if headers is None else headers

	params = params if (type(params) is dict) else params.dict()
	json = json if (type(json) is dict) or type(json) is list else None
	request = requests.Request(method, url, params=params, json=json)
	prepped = request.prepare()
	for h in headers:
		e = h.items()[0]
		prepped.headers[e[0]] = e[1]
	try:
		with Session() as s:
			resp = s.send(prepped, verify=False)

		if resp.status_code == status.HTTP_401_UNAUTHORIZED:
			logger.debug(resp.text)

		if not status.is_success(resp.status_code):
			return Response({"error_message": resp}, status=resp.status_code)
		return Response(resp.json())
	except ValueError:
		# This because if we can't parse a response,
		# it's an html response of Server ERROR
		return Response(
			{"error_message": "Parse error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
	except Exception as e:
		logger.error("Error sending request: %s" % e)
