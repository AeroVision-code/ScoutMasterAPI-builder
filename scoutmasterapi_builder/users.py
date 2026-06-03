import requests


class Users:
    # ── Platform-level user management ──────────────────────────────────────

    def get_all_users(self, page=None, limit=None, order=None, sort_by=None):
        """
        Get all users in the platform (admin only).
        Args:
            page (int, optional): Page number (default 1).
            limit (int, optional): Results per page.
            order (str, optional): 'asc' or 'desc'.
            sort_by (str, optional): 'name', 'email', 'username', or 'created_at'.
        Returns:
            pd.DataFrame or list: Users as DataFrame or JSON list.
        """
        endpoint = "users"
        params = {}
        if page: params["page"] = page
        if limit: params["limit"] = limit
        if order: params["order"] = order
        if sort_by: params["sort_by"] = sort_by
        data = self._get(endpoint, params=params)
        return self._format_output(data)

    def create_user(self, username, email, name=None, phone_number=None, temporary_password=None):
        """
        Create a new user in Cognito (admin only).
        The user is created with FORCE_CHANGE_PASSWORD status.
        Args:
            username (str): Cognito username.
            email (str): User email address.
            name (str, optional): Display name.
            phone_number (str, optional): Phone number.
            temporary_password (str, optional): If omitted, Cognito generates one.
        Returns:
            dict: Created user data.
        """
        payload = {"username": username, "email": email}
        if name: payload["name"] = name
        if phone_number: payload["phone_number"] = phone_number
        if temporary_password: payload["temporary_password"] = temporary_password
        data = self._post("users", payload)
        return data

    def delete_user(self, user_id):
        """
        Delete a user by their Cognito sub (admin only).
        Also removes all project memberships.
        Args:
            user_id (str): Cognito sub of the user.
        Returns:
            dict: Deleted user data.
        """
        data = self._delete(f"users/{user_id}")
        return data

    def enable_user(self, user_id):
        """
        Enable a previously disabled user (admin only).
        Args:
            user_id (str): Cognito sub of the user.
        Returns:
            dict: Updated user data.
        """
        data = self._post(f"users/{user_id}/enable")
        return data

    def disable_user(self, user_id):
        """
        Disable a user — prevents sign-in and invalidates sessions (admin only).
        Args:
            user_id (str): Cognito sub of the user.
        Returns:
            dict: Updated user data.
        """
        data = self._post(f"users/{user_id}/disable")
        return data

    def resend_credentials(self, user_id, temporary_password=None):
        """
        Resend the welcome credentials email to a user (admin only).
        Resets the user's password to a new temporary one.
        Args:
            user_id (str): Cognito sub of the user.
            temporary_password (str, optional): Custom temporary password; auto-generated if omitted.
        Returns:
            dict: Updated user data.
        """
        payload = {}
        if temporary_password: payload["temporary_password"] = temporary_password
        data = self._post(f"users/{user_id}/resend-credentials", payload)
        return data

    # ── Project-scoped user methods ──────────────────────────────────────────

    def project_users(self, project_id, page=None, limit=None, order=None, sort_by=None):
        """
        Get all users who have access to the project.
        Args:
            project_id (str): The ID of the project.
            page (int, optional): Page number.
            limit (int, optional): Results per page.
            order (str, optional): 'asc' or 'desc'.
            sort_by (str, optional): 'name', 'created_at', or 'updated_at'.
        Returns:
            pd.DataFrame or list: Users as DataFrame or JSON list.
        """
        endpoint = f"projects/{project_id}/users"
        params = {}
        if page: params["page"] = page
        if limit: params["limit"] = limit
        if order: params["order"] = order
        if sort_by: params["sort_by"] = sort_by
        data = self._get(endpoint, params=params)
        return self._format_output(data)

    def project_user(self, project_id, user_id):
        """
        Get a single user's membership info within a project.
        Args:
            project_id (str): UUID of the project.
            user_id (str): ID of the user.
        Returns:
            dict: User membership data including role and joined_at.
        """
        endpoint = f"projects/{project_id}/users/{user_id}"
        data = self._get(endpoint)
        return data

    # ── Legacy aliases (kept for backwards compatibility) ───────────────────

    def users(self, project_id):
        """Deprecated: use project_users() instead."""
        return self.project_users(project_id)
