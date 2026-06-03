class Environments:
    # ── Environment CRUD ────────────────────────────────────────────────────

    def environments(self):
        """
        Get all environments accessible to the authenticated user.
        Returns:
            list or DataFrame: Environment records.
        """
        data = self._get("environments")
        return self._format_output(data)

    def environment_by_id(self, environment_id):
        """
        Get a single environment by ID.
        Args:
            environment_id (str): ID of the environment.
        Returns:
            dict: Environment data.
        """
        data = self._get(f"environments/{environment_id}")
        return data

    def environment_create(self, name, description=None):
        """
        Create a new environment (admin only).
        Args:
            name (str): Environment name.
            description (str, optional): Environment description.
        Returns:
            dict: Created environment data.
        """
        payload = {"name": name}
        if description: payload["description"] = description
        data = self._post("environments", payload)
        return data

    def environment_delete(self, environment_id):
        """
        Delete an environment by ID (admin only).
        Args:
            environment_id (str): ID of the environment.
        Returns:
            dict: Deleted environment data.
        """
        data = self._delete(f"environments/{environment_id}")
        return data

    # ── Owners ──────────────────────────────────────────────────────────────

    def environment_owners(self, environment_id):
        """
        List all owners of an environment.
        Args:
            environment_id (str): ID of the environment.
        Returns:
            list or DataFrame: Owner records.
        """
        data = self._get(f"environments/{environment_id}/owners")
        return self._format_output(data)

    def environment_owner_add(self, environment_id, user_id):
        """
        Add a user as an owner of an environment.
        Args:
            environment_id (str): ID of the environment.
            user_id (str): Cognito sub of the user to add as owner.
        Returns:
            dict: Created owner record.
        """
        data = self._post(f"environments/{environment_id}/owners", {"user_id": user_id})
        return data

    def environment_owner_remove(self, environment_id, user_id):
        """
        Remove a user from environment owners.
        Args:
            environment_id (str): ID of the environment.
            user_id (str): Cognito sub of the user to remove.
        Returns:
            dict: Removed owner record.
        """
        data = self._delete(f"environments/{environment_id}/owners/{user_id}")
        return data

    # ── Users ───────────────────────────────────────────────────────────────

    def environment_users(self, environment_id):
        """
        List all users in an environment.
        Args:
            environment_id (str): ID of the environment.
        Returns:
            list or DataFrame: User records.
        """
        data = self._get(f"environments/{environment_id}/users")
        return self._format_output(data)

    def environment_user_add(self, environment_id, user_id=None, email=None,
                              username=None, name=None, phone_number=None,
                              temporary_password=None):
        """
        Add a user to an environment.
        Supply user_id to add an existing user, OR email to create a new Cognito
        user and add them in one call. Exactly one of user_id / email is required.
        Args:
            environment_id (str): ID of the environment.
            user_id (str, optional): Cognito sub of an existing user.
            email (str, optional): Email of a new user to create.
            username (str, optional): Cognito username for the new user (defaults to email).
            name (str, optional): Display name for the new user.
            phone_number (str, optional): Phone number for the new user.
            temporary_password (str, optional): Temporary password for the new user.
        Returns:
            dict: Added environment user record.
        """
        if not user_id and not email:
            raise ValueError("Provide either user_id (existing user) or email (new user).")
        payload = {}
        if user_id: payload["user_id"] = user_id
        if email: payload["email"] = email
        if username: payload["username"] = username
        if name: payload["name"] = name
        if phone_number: payload["phone_number"] = phone_number
        if temporary_password: payload["temporary_password"] = temporary_password
        data = self._post(f"environments/{environment_id}/users", payload)
        return data

    def environment_user_remove(self, environment_id, user_id):
        """
        Remove a user from an environment.
        Args:
            environment_id (str): ID of the environment.
            user_id (str): Cognito sub of the user to remove.
        Returns:
            dict: Removed user record.
        """
        data = self._delete(f"environments/{environment_id}/users/{user_id}")
        return data

    # ── Projects ─────────────────────────────────────────────────────────────

    def environment_projects(self, environment_id):
        """
        List all projects in an environment.
        Args:
            environment_id (str): ID of the environment.
        Returns:
            list or DataFrame: Project records.
        """
        data = self._get(f"environments/{environment_id}/projects")
        return self._format_output(data)

    def environment_project_add(self, environment_id, project_id):
        """
        Add a project to an environment.
        Args:
            environment_id (str): ID of the environment.
            project_id (str): UUID of the project to add.
        Returns:
            dict: Added project record.
        """
        data = self._post(f"environments/{environment_id}/projects/{project_id}")
        return data

    def environment_project_remove(self, environment_id, project_id):
        """
        Remove a project from an environment.
        Args:
            environment_id (str): ID of the environment.
            project_id (str): UUID of the project to remove.
        Returns:
            dict: Removed project record.
        """
        data = self._delete(f"environments/{environment_id}/projects/{project_id}")
        return data

    # ── Services ─────────────────────────────────────────────────────────────

    def environment_services(self, environment_id):
        """
        List all services enabled for an environment.
        Args:
            environment_id (str): ID of the environment.
        Returns:
            list or DataFrame: Service records.
        """
        data = self._get(f"environments/{environment_id}/services")
        return self._format_output(data)

    def environment_service_add(self, environment_id, service_id):
        """
        Add a service to an environment.
        Args:
            environment_id (str): ID of the environment.
            service_id (int): Numeric ID of the service.
        Returns:
            dict: Added service record.
        """
        data = self._post(f"environments/{environment_id}/services/{service_id}")
        return data

    def environment_service_remove(self, environment_id, service_id):
        """
        Remove a service from an environment.
        Args:
            environment_id (str): ID of the environment.
            service_id (int): Numeric ID of the service.
        Returns:
            dict: Removed service record.
        """
        data = self._delete(f"environments/{environment_id}/services/{service_id}")
        return data
