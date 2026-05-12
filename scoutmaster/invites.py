class Invites:
    def project_invite_send(self, project_id, email, role, message=None):
        """
        Send a project invitation to a user by email.

        Args:
            project_id (str): UUID of the project.
            email (str): Email address of the invitee.
            role (str): Role to assign — 'member' or 'owner'.
            message (str, optional): Personal message to include in the invite.

        Returns:
            dict: Contains 'invite_id' and 'message'.
        """
        if role not in ("member", "owner"):
            raise ValueError("role must be 'member' or 'owner'")
        endpoint = f"projects/{project_id}/invites"
        payload = {"email": email, "role": role, "message": message}
        data = self._post(endpoint, payload)
        return data

    def project_invites(self, project_id):
        """
        List all pending invites for a project.

        Args:
            project_id (str): UUID of the project.

        Returns:
            list or DataFrame: Invite records.
        """
        endpoint = f"projects/{project_id}/invites"
        data = self._get(endpoint)
        return self._format_output(data)

    def project_invite_resend(self, project_id, email):
        """
        Resend an existing invite to a user.

        Args:
            project_id (str): UUID of the project.
            email (str): Email address the invite was originally sent to.

        Returns:
            dict: Contains 'invite_id' and 'message'.
        """
        endpoint = f"projects/{project_id}/invites/resend"
        data = self._post(endpoint, {"email": email})
        return data

    def invite_validate(self, token):
        """
        Validate an invite token — returns project, email, role and expiry.

        Args:
            token (str): The invite token from the invite link.

        Returns:
            dict: Invite validation data including project details and role.
        """
        endpoint = f"invites/{token}/validate"
        data = self._get(endpoint)
        return data

    def invite_accept(self, token):
        """
        Accept a project invite using its token.

        Args:
            token (str): The invite token from the invite link.

        Returns:
            dict: Contains 'role', 'project_id' and 'message'.
        """
        endpoint = f"invites/{token}/accept"
        data = self._post(endpoint)
        return data

    def my_invites(self):
        """
        List all pending invites for the currently authenticated user.

        Returns:
            list or DataFrame: Invite records including project details.
        """
        endpoint = "users/me/invites"
        data = self._get(endpoint)
        return self._format_output(data)
