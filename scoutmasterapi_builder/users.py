import requests

from .base import conceptual


class Users:
    # ── Own account / user lookup ───────────────────────────────────────────

    def user_me(self):
        """
        Get the authenticated user's own account, including their profile
        image (image_path).
        Returns:
            dict: User data.
        """
        data = self._get("users/me")
        return data

    def user_by_id(self, user_id):
        """
        Get a single user by id, including their profile image (image_path).
        Accessible by admin clients, platform admins, or the user themselves.
        Args:
            user_id (str): Cognito sub of the user.
        Returns:
            dict: User data.
        """
        data = self._get(f"users/{user_id}")
        return data

    def user_upload_image(self, user_id, file_path):
        """
        Upload a profile image for a user.
        Accessible by admin clients, platform admins, or the user themselves.
        Args:
            user_id (str): Cognito sub of the user.
            file_path (str): Local path to the image.
        Returns:
            dict: Updated user data.
        """
        return self._post_file(f"users/{user_id}/image", file_path)

    # ── Platform-level user management ──────────────────────────────────────

    @conceptual
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
        data = self._get_paged(endpoint, params=params)
        return self._format_output(data)

    @conceptual
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

    @conceptual
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

    @conceptual
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

    @conceptual
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

    @conceptual
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

    @conceptual
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
        data = self._get_paged(endpoint, params=params)
        return self._format_output(data)

    @conceptual
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

    @conceptual
    def project_user_remove(self, project_id, user_id):
        """
        Remove a user from a project. Owners can remove anyone; members can
        only remove themselves. The removed user's collections are handed over
        to a remaining owner.
        Args:
            project_id (str): UUID of the project.
            user_id (str): ID of the user.
        Returns:
            dict: Response data.
        """
        endpoint = f"projects/{project_id}/users/{user_id}"
        data = self._delete(endpoint)
        return data

    # ── Legacy aliases (kept for backwards compatibility) ───────────────────

    def users(self, project_id):
        """Deprecated: use project_users() instead."""
        return self.project_users(project_id)
