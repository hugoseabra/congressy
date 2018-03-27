import re
from datetime import timedelta

import absoluteuri
from django.conf import settings
from django.db import models
from django.utils import six, timezone
from jsonfield import JSONField

from bitly.client import BitlyClient
from .conf import BITLY_TIMEOUT_STATS
from .exceptions import BittleException


class BittleManager(models.Manager):
    """
    Custom manager for the ``Bittle`` model.

    Defines methods to provide shortcuts for creation and management of
    Bit.ly links to local objects.
    """

    def filter_for_instance(self, obj):
        app_label = obj._meta.app_label
        model = obj._meta.model_name
        return self.filter(
            content_type__app_label=app_label,
            content_type__model=model, object_id=obj.pk,
        )

    def bitlify(self, link):
        """
        Creates a new ``Bittle`` object based on the object passed to it.
        The object must have a ``get_absolute_url`` in order for this to
        work.
        """
        # If the object does not have a get_absolute_url() method or the
        # Bit.ly API authentication settings are not in settings.py, fail.
        if not (settings.BITLY_LOGIN and settings.BITLY_API_KEY):
            raise BittleException("Bit.ly credentials not found in settings.")

        if not isinstance(link, six.string_types):
            raise BittleException(
                "Failed: you must provided a string as link."
            )

        noslash_scheme = 'aim|apt|bitcoin|callto|cid|data|dav|fax|feed|geo|'
        noslash_scheme += 'go|h323|iax|im|magnet|mailto|message|mid|msnim|mvn|'
        noslash_scheme += 'news|palm|paparazzi|pres|proxy|query|session|sip|'
        noslash_scheme += 'sips|skype|sms|spotify|steam|tag|tel|things|urn|'
        noslash_scheme += 'uuid|view-source|ws|wyciwyg|xmpp|ymsgr'

        if re.match(r'^(' + noslash_scheme + '):', link, re.IGNORECASE):
            # These are the URI Schemes that can be legitimately used with
            # no slashes: http://en.wikipedia.org/wiki/URI_scheme
            # Treat these as ready-to-go
            url = link
        elif re.match(r'(attachment|platform):/', link, re.IGNORECASE):
            # These can be used with only one forward slash
            # Treat these as ready-to-go
            url = link
        elif re.match(r'^https?://', link, re.IGNORECASE):
            # This is an HTTP link, just send it through.
            url = link
        elif re.match(r'^[^:/]+://', link, re.IGNORECASE):
            # These are meant to be used with double-forward-slashes
            # Treat these as ready-to-go
            url = link
        elif re.match(r'^//', link, re.IGNORECASE):
            # If this is schemeless, fully-qualified URL, sometimes used to
            # avoid mixed-scheme webpage issues (particularly, http/https
            # security issues).  We'll need an actual scheme for this though,
            # so we'll use whatever they pass into the kwarg: scheme.
            url = "http:{}".format(link)
        else:
            url = absoluteuri.build_absolute_uri(link)

        try:
            bittle = self.get(absolute_url=url)

        except self.model.DoesNotExist:
            client = BitlyClient()
            results = client.shorten(url)

            if results.get('error'):
                raise BittleException('It was not possible to generate link.')

            bittle = Bittle.objects.create(
                absolute_url=url,
                shortUrl=results.get('url'),
                hash=results.get('hash'),
            )

        return bittle


class Bittle(models.Model):
    """An object representing a Bit.ly link to a local object."""

    absolute_url = models.URLField(max_length=1024)
    hash = models.CharField(max_length=10)
    short_url = models.URLField()
    _clicks = models.PositiveIntegerField(
        blank=True,
        editable=False,
        db_column='click',
    )
    _referrers = JSONField(blank=True, editable=False)
    check_stamp = models.DateTimeField(blank=True, null=True, editable=False)

    # Timestamps
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    objects = BittleManager()

    class Meta:
        ordering = ("-created",)

    def __str__(self):
        return self.hash

    @property
    def clicks(self):
        self._update_stats()
        return self._clicks

    @property
    def referrers(self):
        self._update_stats()

        class Referrer:
            def __init__(self, name, bitly_link, referrer_link, clicks):
                self.name = name
                self.bitly_link = bitly_link
                self.referrer_link = referrer_link
                self.clicks = int(clicks)

            def __str__(self):
                return 'Referrer ' + self.name

        referrers = []
        for name, refs in six.iteritems(self.referrers):
            for item in six.iteritems(refs):
                referrers.append(Referrer(
                    name=name,
                    bitly_link=self.short_url,
                    referrer_link=item.get('referrer'),
                    clicks=item.get('clicks')
                ))

        return referrers

    def _update_stats(self):
        timeout = timedelta(minutes=BITLY_TIMEOUT_STATS)
        now = timezone.now()

        if self.check_stamp is not None and now - self.check_stamp > timeout:
            client = BitlyClient()
            self._clicks = int(client.clicks(link=self.short_url))
            self._referrers = client.referrers(link=self.short_url)
            self.check_stamp = now
            self.save()
