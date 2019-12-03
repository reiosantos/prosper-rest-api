from rest_framework import relations


class FilterByVenueMixin:

    def filter_by_venue(self, queryset):
        return queryset.filter(venue=self._venue)

    # noinspection PyUnresolvedReferences
    @property
    def _venue(self):
        return self.context['request'].venue


class ForThisVenueManyRelatedField(FilterByVenueMixin, relations.ManyRelatedField):
    """
    A PrimaryKeyRelatedField with a queryset filtered by the serializer's
    Venue.  Assumes that the serializer has a 'request' in its context, and
    that that request has a 'venue' attribute.
    """

    # noinspection PyUnresolvedReferences
    def get_queryset(self):
        queryset = super(ForThisVenueManyRelatedField, self).get_queryset()
        return self.filter_by_venue(queryset)

    def to_representation(self, iterable):
        venue = self._venue
        return super(ForThisVenueManyRelatedField, self).to_representation([
            value for value in iterable if value.venue == venue
        ])

    def to_internal_value(self, data):
        """
        Ensures that values relating to other venues remain unaffected.
        """

        internal_value = super(ForThisVenueManyRelatedField, self).to_internal_value(data)

        if self.parent and self.parent.instance:
            values_from_other_venues = getattr(self.parent.instance, self.source) \
                .exclude(venue=self._venue)
            internal_value += list(values_from_other_venues)

        return internal_value


class ForThisVenuePrimaryKeyRelatedField(FilterByVenueMixin, relations.PrimaryKeyRelatedField):
    """
    A PrimaryKeyRelatedField with a queryset filtered by the serializer's
    Venue.  Assumes that the serializer has a 'request' in its context, and
    that that request has a 'venue' attribute.
    """

    def get_queryset(self):
        queryset = super(ForThisVenuePrimaryKeyRelatedField, self).get_queryset()

        return self.filter_by_venue(queryset)

    @classmethod
    def many_init(cls, *args, **kwargs):
        """
        This method handles creating a parent `ManyRelatedField` instance
        when the `many=True` keyword argument is passed.

        Typically you won't need to override this method.

        Note that we're over-cautious in passing most arguments to both parent
        and child classes in order to try to cover the general case. If you're
        overriding this method you'll probably want something much simpler, eg:

        @classmethod
        def many_init(cls, *args, **kwargs):
            kwargs['child'] = cls()
            return CustomManyRelatedField(*args, **kwargs)
        """
        list_kwargs = {'child_relation': cls(**kwargs)}
        for key in kwargs.keys():
            if key in relations.MANY_RELATION_KWARGS:
                list_kwargs[key] = kwargs[key]
        return ForThisVenueManyRelatedField(**list_kwargs)
