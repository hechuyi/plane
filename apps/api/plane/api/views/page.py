# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from plane.api.middleware.api_authentication import APIKeyAuthentication
from plane.api.rate_limit import ApiKeyRateThrottle
from plane.app.views import PageViewSet as AppPageViewSet
from plane.app.views import PagesDescriptionViewSet as AppPagesDescriptionViewSet


class APIKeyPageMixin:
    authentication_classes = [APIKeyAuthentication]

    def get_throttles(self):
        return [ApiKeyRateThrottle()]


class PageViewSet(APIKeyPageMixin, AppPageViewSet):
    """Project page endpoints exposed through the public API key surface."""


class PagesDescriptionViewSet(APIKeyPageMixin, AppPagesDescriptionViewSet):
    """Project page description endpoint exposed through the public API key surface."""
