# Copyright (c) 2023-present Plane Software, Inc. and contributors
# SPDX-License-Identifier: AGPL-3.0-only
# See the LICENSE file for details.

from unittest import mock

import pytest
from rest_framework import status

from plane.db.models import Page, Project, ProjectMember, ProjectPage


@pytest.fixture
def project(db, workspace, create_user):
    """Create a test project with the API token user as a member."""
    project = Project.objects.create(
        name="Test Project",
        identifier="TP",
        workspace=workspace,
        created_by=create_user,
    )
    ProjectMember.objects.create(
        project=project,
        member=create_user,
        role=20,
        is_active=True,
    )
    return project


@pytest.mark.contract
class TestProjectPageListCreateAPIEndpoint:
    """Contract tests for /api/v1/workspaces/{slug}/projects/{project_id}/pages/."""

    def get_url(self, workspace_slug, project_id):
        return f"/api/v1/workspaces/{workspace_slug}/projects/{project_id}/pages/"

    @pytest.mark.django_db
    def test_create_page_with_api_key(self, api_key_client, workspace, project, create_user):
        url = self.get_url(workspace.slug, project.id)
        payload = {
            "name": "API Page",
            "description_html": "<p>Created from the public API.</p>",
        }

        with mock.patch("plane.app.views.page.base.page_transaction.delay") as page_transaction_delay:
            response = api_key_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED, f"Got {response.status_code}: {response.data!r}"
        page = Page.objects.get(id=response.data["id"])
        assert page.name == payload["name"]
        assert page.description_html == payload["description_html"]
        assert page.owned_by == create_user
        assert ProjectPage.objects.filter(project=project, page=page, workspace=workspace).exists()
        page_transaction_delay.assert_called_once()

    @pytest.mark.django_db
    def test_list_pages_with_api_key(self, api_key_client, workspace, project, create_user):
        page = Page.objects.create(
            name="Existing Page",
            description_html="<p>Existing content.</p>",
            workspace=workspace,
            owned_by=create_user,
        )
        ProjectPage.objects.create(project=project, page=page, workspace=workspace)

        response = api_key_client.get(self.get_url(workspace.slug, project.id))

        assert response.status_code == status.HTTP_200_OK, f"Got {response.status_code}: {response.data!r}"
        assert len(response.data) == 1
        assert response.data[0]["id"] == page.id
