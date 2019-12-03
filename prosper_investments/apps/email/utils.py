from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail.message import EmailMessage
from django.http import QueryDict
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.urls import reverse

from prosper_investments.apps.common.templatetags.filters import translate_for_venue
from prosper_investments.apps.user.utils import UserCustomTemplate
from prosper_investments.apps.venue.models import Venue


class EmailAddressee:
	def __init__(self, address, name=None):
		self.address = address
		self.name = name

	def address_with_name(self):
		"""
		Name <address>
		"""
		if self.name:
			return '%s <%s>' % (self.name, self.address)
		return self.address


class TemplateMixin:
	default_template_name = ''

	@property
	def template_name(self):
		template_name = self.default_template_name
		try:
			# noinspection PyUnresolvedReferences
			template_name = '%s/%s' % (self.instance.venue.url_component, template_name)
			get_template('email/%s.html' % template_name)
			return template_name
		except TemplateDoesNotExist:
			pass
		return self.default_template_name


class BaseEmailMessage(EmailMessage):
	content_subtype = 'html'
	"""
	Checklist email message.
	"""

	def __init__(self, subject, to, body):
		super(BaseEmailMessage, self).__init__(
			subject=subject,
			to=to,
			from_email=self.get_from_address,
			reply_to=self.get_default_reply_address,
			body=body
		)

	@property
	def get_from_address(self):
		return settings.DEFAULT_FROM_EMAIL

	@property
	def get_default_reply_address(self):
		return [settings.DEFAULT_SUPPORT_EMAIL]


class CustomEmailMessage(BaseEmailMessage):
	# noinspection PyBroadException
	def __init__(self):
		to = list(map(lambda r: r.address_with_name(), self._addressees()))
		# noinspection PyUnresolvedReferences
		super(CustomEmailMessage, self).__init__(
			subject=self.get_subject(), to=to, body=self.get_body())

	@property
	def template_name(self):
		"""
		Name of the template.
		"""
		raise NotImplementedError('template_name must be defined')

	def _addressees(self):

		if not self.addressees:
			return []

		addresses = list(filter(
			lambda x: x is not None and x.address is not None, self.addressees))

		self.failures = list(filter(
			lambda x: x is None or x.address is None, self.addressees))

		# deduplicate the list
		seen = set()
		unique = []
		for a in addresses:
			if a.address not in seen:
				unique.append(a)
				seen.add(a.address)
		addresses = unique
		self.successes = addresses
		return addresses

	@property
	def addressees(self):
		"""
		The recipients.
		"""
		return self.get_addressees()

	def get_addressees(self):
		raise NotImplementedError('The recipient(s) must be defined')

	def send(self, fail_silently=False):
		"""Sends the email message."""
		if not self.recipients():
			# Don't bother creating the network connection if there's nobody to
			# send to.
			return 0
		return self.get_connection(fail_silently).send_messages([self])


class ContextEmailMessage(CustomEmailMessage):
	"""
	Template email.
	"""

	@property
	def template_name(self):
		return super(ContextEmailMessage, self).template_name

	def get_addressees(self):
		return super(ContextEmailMessage, self).get_addressees()

	# noinspection PyBroadException
	def __init__(self, model_instance, context=None):
		self.instance = model_instance
		self.context = context
		super(ContextEmailMessage, self).__init__()

	def get_body(self):
		request = self.context['request']
		self.context['browser_name'] = request.META.get('HTTP_USER_AGENT', 'Unknown')
		return get_template('email/%s.html' % self.template_name).render({
			'instance': self.instance,
			'DEFAULT_SUPPORT_EMAIL': settings.DEFAULT_SUPPORT_EMAIL,
			'context': self.context
		})

	def get_reply_address(self):
		"""
		Try to get the email address from the context's Venue
		"""
		request = self.context.get('request')
		if request and request.venue:
			return request.venue.support_email_address

		return self.get_default_reply_address


class WelcomeEmail(ContextEmailMessage):
	"""
	An email which is sent when a user signs up
	"""
	# placeholder until users are associated with different industries
	template_name = Venue.WELCOME_TEMPLATE

	def get_subject(self):
		return 'Welcome to Prosper Investments'

	def get_addressees(self):
		return [EmailAddressee(self.instance.email, self.instance.full_name)]


class VerifyUserEmail(ContextEmailMessage):
	"""
	An email which is sent when a usercreate a new account
	"""
	template_name = 'psp-email-verification'

	def get_subject(self):
		return 'Email Verification for Prosper Investments'

	def get_addressees(self):
		return [EmailAddressee(self.instance.email, self.instance.full_name)]


def site_url(request, uri):
	"""
	Append the current site protocol and url to the given uri.
	"""
	site = get_current_site(request)
	if site is not None:
		return '{0}://{1}{2}{3}'.format(
			'https' if settings.SSL_ENABLED else 'http',
			site.name,
			'' if uri.startswith('/') else '/',
			uri
		)
	return site


# @TODO? handle `site is None`


def get_password_reset_link(request, address):
	querystring = QueryDict('', mutable=True)
	querystring['email'] = address
	uri = '%s?%s' % (reverse('password_reset_form'), querystring.urlencode())
	return site_url(request, uri)


class CardErrorEmail(TemplateMixin, ContextEmailMessage):
	template_name = 'vc5-card-error'

	def get_subject(self):
		return 'Card Error'

	def get_addressees(self):
		return [
			EmailAddressee(self.context.get('user_email', None),
			               self.context.get('user_name', None)),
			EmailAddressee(self.context.get('venue_admin_email', None)),
			EmailAddressee(settings.ADMIN_EMAIL)]


class RoleTemplateMixin:

	# noinspection PyUnresolvedReferences
	@property
	def template_name(self):
		template_name = self.default_template_name
		try:
			template_name = '%s/%s' % (
				self.context['request'].venue.url_component, template_name)
			get_template('email/%s.html' % template_name)
			return template_name
		except TemplateDoesNotExist:
			pass
		return self.default_template_name


class NewRoleEmail(RoleTemplateMixin, BaseEmailMessage):
	"""
	An email for when a booking is completed
	"""
	default_template_name = 'psp-new-role'

	def __init__(self, instance, context):
		self.instance = instance
		self.context = context

		super(NewRoleEmail, self).__init__(
			subject=translate_for_venue('EMAIL_newRole', self.context['request'].venue),
			to=[instance.email],
			body=self.get_body()
		)

	def get_body(self):
		return get_template('email/%s.html' % self.template_name).render({
			'instance': self.instance,
			'context': self.context,
			'msg': UserCustomTemplate(self.instance).render(
				self.context['role'].email_template
			)
		})
