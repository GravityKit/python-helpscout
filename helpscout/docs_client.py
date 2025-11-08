from __future__ import annotations

import logging
from typing import Any

import requests
from requests.auth import HTTPBasicAuth

from helpscout.exceptions import (
    HelpScoutAuthenticationException,
    HelpScoutException,
)

logger = logging.getLogger('HelpScoutDocs')


class HelpScoutDocs:
    """Help Scout Docs API v1 client wrapper.

    The Docs API uses Basic Auth with the API key as username, unlike the
    Mailbox API which uses OAuth2.

    Parameters
    ----------
    api_key: str
        The Docs API key from Help Scout
    base_url: str
        The Docs API base URL (default: https://docsapi.helpscout.net/v1/)
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = 'https://docsapi.helpscout.net/v1/',
    ) -> None:
        if not api_key:
            raise HelpScoutAuthenticationException('Docs API key is required')

        self.api_key = api_key
        self.base_url = base_url.rstrip('/') + '/'
        self.auth = HTTPBasicAuth(self.api_key, 'X')  # Basic Auth with API key as username

    def _headers(self) -> dict[str, str]:
        """Returns headers for Docs API (not including auth, handled by requests)."""
        return {
            'Content-Type': 'application/json',
        }

    def create_article(
        self,
        collection_id: str,
        name: str,
        text: str,
        status: str = 'notpublished',
        categories: list[str] | None = None,
        tags: list[str] | None = None,
        related_articles: list[str] | None = None,
        slug: str | None = None,
    ) -> dict[str, Any]:
        """Create a new article in Help Scout Docs.

        Parameters
        ----------
        collection_id: str
            The collection ID where the article will be created
        name: str
            Article title/name
        text: str
            Article content (HTML or Markdown)
        status: str
            Article status ('published', 'notpublished', or 'draft')
        categories: list[str] | None
            List of category IDs to assign the article to
        tags: list[str] | None
            List of tags for the article
        related_articles: list[str] | None
            List of related article IDs
        slug: str | None
            Custom URL slug for the article

        Returns
        -------
        dict
            Created article data from the API
        """
        url = f'{self.base_url}articles'

        data: dict[str, Any] = {
            'collectionId': collection_id,
            'name': name,
            'text': text,
            'status': status,
        }

        if categories:
            data['categories'] = categories
        if tags:
            data['tags'] = tags
        if related_articles:
            data['related'] = related_articles
        if slug:
            data['slug'] = slug

        logger.debug(f'POST {url}')
        response = requests.post(url, headers=self._headers(), json=data, auth=self.auth, timeout=30)

        if response.ok:
            # Help Scout Docs API may return 201 with empty body or Location header
            if response.status_code == 201 and not response.text:
                # Extract article ID from Location header if available
                location = response.headers.get('Location', '')
                article_id = location.split('/')[-1] if location else None
                return {'id': article_id, 'status': 'created'}
            try:
                return response.json()
            except ValueError:
                # If response can't be parsed as JSON, return basic info
                return {'status_code': response.status_code, 'text': response.text}
        else:
            raise HelpScoutException(
                f'Failed to create article: {response.status_code} - {response.text}'
            )

    def update_article(
        self,
        article_id: str,
        name: str | None = None,
        text: str | None = None,
        status: str | None = None,
        categories: list[str] | None = None,
        tags: list[str] | None = None,
        related_articles: list[str] | None = None,
        slug: str | None = None,
    ) -> dict[str, Any]:
        """Update an existing article in Help Scout Docs.

        Parameters
        ----------
        article_id: str
            The article ID to update
        name: str | None
            New article title/name (optional)
        text: str | None
            New article content (optional)
        status: str | None
            New status (optional)
        categories: list[str] | None
            New category IDs (optional)
        tags: list[str] | None
            New tags (optional)
        related_articles: list[str] | None
            New related article IDs (optional)
        slug: str | None
            New URL slug (optional)

        Returns
        -------
        dict
            Updated article data from the API
        """
        url = f'{self.base_url}articles/{article_id}'

        data: dict[str, Any] = {}

        if name is not None:
            data['name'] = name
        if text is not None:
            data['text'] = text
        if status is not None:
            data['status'] = status
        if categories is not None:
            data['categories'] = categories
        if tags is not None:
            data['tags'] = tags
        if related_articles is not None:
            data['related'] = related_articles
        if slug is not None:
            data['slug'] = slug

        if not data:
            raise ValueError('At least one field must be provided for update')

        logger.debug(f'PUT {url}')
        response = requests.put(url, headers=self._headers(), json=data, auth=self.auth, timeout=30)

        if response.ok:
            return response.json()
        else:
            raise HelpScoutException(
                f'Failed to update article: {response.status_code} - {response.text}'
            )

    def get_article(self, article_id: str) -> dict[str, Any]:
        """Get an article by ID.

        Parameters
        ----------
        article_id: str
            The article ID to retrieve

        Returns
        -------
        dict
            Article data from the API
        """
        url = f'{self.base_url}articles/{article_id}'

        logger.debug(f'GET {url}')
        response = requests.get(url, headers=self._headers(), auth=self.auth, timeout=30)

        if response.ok:
            return response.json()
        else:
            raise HelpScoutException(
                f'Failed to get article: {response.status_code} - {response.text}'
            )

    def delete_article(self, article_id: str) -> None:
        """Delete an article.

        Parameters
        ----------
        article_id: str
            The article ID to delete
        """
        url = f'{self.base_url}articles/{article_id}'

        logger.debug(f'DELETE {url}')
        response = requests.delete(url, headers=self._headers(), auth=self.auth, timeout=30)

        if not response.ok:
            raise HelpScoutException(
                f'Failed to delete article: {response.status_code} - {response.text}'
            )

    def __repr__(self) -> str:
        """Returns the object as a string."""
        return f'{self.__class__.__name__}(base_url="{self.base_url}")'

    __str__ = __repr__
