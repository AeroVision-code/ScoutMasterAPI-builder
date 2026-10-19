class Webhooks:
    def project_webhook(self, project_id):
        """
        Get the project's configured webhook URL.
        The signing secret is never returned here; only by
        project_webhook_set() (first time) or project_webhook_rotate_secret().
        Args:
            project_id (str): UUID of the project.
        Returns:
            dict: Webhook data ({"url": ...}).
        """
        endpoint = f"projects/{project_id}/webhook"
        data = self._get(endpoint)
        return data

    def project_webhook_set(self, project_id, url):
        """
        Create or replace the project's webhook URL.
        The first time a webhook is set up, a signing secret is generated and
        returned once in this response — store it immediately. Changing the
        URL later leaves the existing secret untouched.
        Args:
            project_id (str): UUID of the project.
            url (str): URL to notify (via POST) when one of the project's
                fields, layers or subscriptions changes.
        Returns:
            dict: Webhook data ({"url": ..., "secret": ...}).
        """
        endpoint = f"projects/{project_id}/webhook"
        data = self._put(endpoint, {"url": url})
        return data

    def project_webhook_delete(self, project_id):
        """
        Remove the project's webhook entirely.
        Args:
            project_id (str): UUID of the project.
        Returns:
            bool: True if the webhook was deleted (204 No Content).
        """
        endpoint = f"projects/{project_id}/webhook"
        return self._delete(endpoint)

    def project_webhook_rotate_secret(self, project_id):
        """
        Rotate the webhook's signing secret, invalidating the old one.
        The new secret is returned once in this response.
        Args:
            project_id (str): UUID of the project.
        Returns:
            dict: Webhook data ({"url": ..., "secret": ...}).
        """
        endpoint = f"projects/{project_id}/webhook/rotate-secret"
        data = self._post(endpoint)
        return data
