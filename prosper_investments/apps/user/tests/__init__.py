from itertools import chain, combinations

from rest_framework.test import APITestCase

from prosper_investments.apps.venue.models import User


class LoggedInAPITestCase(APITestCase):
    """
    A test case in which a given user is logged in in setup, and the user is logged out in teardown.
    """

    # Default pk of user to log in
    user_pk = 1

    def get_user(self):
        """
        Get the user to log in.
        """
        return User.objects.filter(pk=self.user_pk).get()

    def setUp(self):
        user = self.get_user()
        self.client.force_authenticate(user=user)

    def tearDown(self):
        self.client.force_authenticate(user=None)

    # returns the powerset of an iterable minus sets of length 1 or len(iterable) -
    # useful for checking all possible combos of fields
    # Author: Fraser E-S
    def powerset(self, iterable):
        iter_list = list(iterable)
        return chain.from_iterable(combinations(iter_list, n) for n in range(1, len(iter_list)))

    # used to add the results of powerset together into a single dicts
    # Author: Fraser E-S
    def combine_dicts(self, list_of_dicts):
        return_dict = {}
        for dict_ in list_of_dicts:
            for key, value in dict_.items():
                return_dict[key] = value
        return return_dict

    def json_post(self, url, data=None):
        return self.client.post(url, data, format='json')


class UnauthenticatedAPITestCase(APITestCase):
    """
    A test case in which a user is unauthenticated.
    """

    def setUp(self):
        self.client.force_authenticate(user=None)

    def tearDown(self):
        pass

    def user_is_blocked(self, url, get=401, post=401, put=401, patch=401, delete=401):
        """
        checks that the given url returns the specifed responses.
        """
        get_response = self.client.get(url)
        self.assertEqual(get_response.status_code, get,
                         "GET gave a {0} status code rather than a {1} for the {2} url".format(
                             get_response.status_code,
                             get, url))

        post_response = self.client.post(url)
        self.assertEqual(post_response.status_code, post,
                         "POST gave a {0} status code rather than a {1} for the {2} url".format(
                             post_response.status_code, post, url))

        put_response = self.client.put(url)
        self.assertEqual(put_response.status_code, put,
                         "PUT gave a {0} status code rather than a {1} for the {2} url".format(
                             put_response.status_code,
                             put, url))

        patch_response = self.client.patch(url)
        self.assertEqual(patch_response.status_code, patch,
                         "PATCH gave a {0} status code rather than a {1} for the {2} url".format(
                             patch_response.status_code, patch, url))

        delete_response = self.client.delete(url)
        self.assertEqual(delete_response.status_code, delete,
                         "DELETE gave a {0} status code rather than a {1} for the {2} url".format(
                             delete_response.status_code, delete, url))

    def json_post(self, url, data=None):
        return self.client.post(url, data, format='json')

    def powerset(self, iterable):
        iter_list = list(iterable)
        return chain.from_iterable(combinations(iter_list, n) for n in range(1, len(iter_list)))

    # used to add the results of powerset together into a single dicts
    def combine_dicts(self, list_of_dicts):
        return_dict = {}
        for dict_ in list_of_dicts:
            for key, value in dict_.items():
                return_dict[key] = value
        return return_dict
