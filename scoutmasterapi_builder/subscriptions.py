class Subscriptions:
    def subscriptions_by_project(self, project_id, page=None, limit=None, order=None, sort_by=None):
        """
        Get all subscriptions for a project.
        Args:
            project_id (str): UUID of the project.
            page (int, optional): Page number (default 1).
            limit (int, optional): Results per page.
            order (str, optional): 'asc' or 'desc'.
            sort_by (str, optional): 'created_at' or 'updated_at'.
        Returns:
            DataFrame or dict: Paginated subscriptions.
        """
        endpoint = f"projects/{project_id}/subscriptions"
        params = {}
        if page: params["page"] = page
        if limit: params["limit"] = limit
        if order: params["order"] = order
        if sort_by: params["sort_by"] = sort_by
        data = self._get(endpoint, params=params)
        return self._format_output(data)

    def subscriptions_by_field(self, field_id):
        """
        Get all subscriptions for a field.
        Args:
            field_id (str): UUID of the field.
        Returns:
            list or DataFrame: Subscriptions for the field.
        """
        endpoint = f"fields/{field_id}/subscriptions"
        data = self._get(endpoint)
        return self._format_output(data)

    def subscription_create(self, field_id, user_id, subscription_id, started_at=None, ended_at=None):
        """
        Create a subscription for a field.
        Args:
            field_id (str): UUID of the field.
            user_id (str): ID of the user.
            subscription_id (int): Numeric subscription type ID.
            started_at (str, optional): ISO8601 start timestamp.
            ended_at (str, optional): ISO8601 end timestamp.
        Returns:
            list or dict: Created subscription data.
        """
        endpoint = f"fields/{field_id}/subscriptions"
        payload = {"user_id": user_id, "subscription_id": subscription_id}
        if started_at: payload["started_at"] = started_at
        if ended_at: payload["ended_at"] = ended_at
        data = self._post(endpoint, payload)
        return data
