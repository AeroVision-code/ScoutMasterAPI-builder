from .base import conceptual_class


@conceptual_class
class Eid:
    """eID / eVault (W3DS) integration.

    The browser sign-in endpoints (login-offer, signup, signup/verify,
    deeplink-result and the wallet callback) are left out: they are called by
    the frontend or the wallet app, not by an API client.
    """

    # ── Account link ─────────────────────────────────────────────────────────

    def eid_offer(self):
        """
        Create a W3DS sign-in offer to link the authenticated user's eID.
        Returns:
            dict: {"uri": ..., "sessionId": ...}; render `uri` as a QR code.
        """
        return self._get("eid/offer")

    def eid_status(self):
        """
        Get the eID link status of the authenticated user.
        Returns:
            dict: {"connected": bool, "ename": ..., "connectedAt": ...}
        """
        return self._get("eid/status")

    def eid_unlink(self):
        """
        Remove the eID link from the authenticated user's account.
        Returns:
            dict: Response data.
        """
        return self._delete("eid/link")

    def eid_sync_avatar(self):
        """
        Write the authenticated user's profile picture into their eVault.
        Returns:
            dict: Response data.
        """
        return self._post("eid/sync-avatar")

    # ── Fields ───────────────────────────────────────────────────────────────

    def eid_sync_fields(self, project_id):
        """
        Pull field data from the eVault into a project.
        Args:
            project_id (str): UUID of the project.
        Returns:
            dict: Response data.
        """
        return self._post("eid/sync-fields", {"projectId": project_id})

    def eid_synced_fields(self):
        """
        Get the ids of the caller's fields that are in their owner's eVault.
        Returns:
            dict: {"fieldIds": [...]}
        """
        return self._get("eid/synced-fields")

    def eid_vault_fields(self, project_id):
        """
        Get the parcels other platforms (FarmMaps) wrote into the caller's
        eVault, and whether each one is in the project already; for picking
        which ones to import with eid_sync_fields().
        Args:
            project_id (str): UUID of the project.
        Returns:
            dict: {"fields": [...]}
        """
        return self._get("eid/vault-fields", params={"projectId": project_id})

    def eid_field_owners(self):
        """
        Get who each of the caller's fields belongs to and whether that person
        has an eID linked.
        Returns:
            Response data.
        """
        return self._get("eid/field-owners")

    def eid_field_history(self, field_id):
        """
        Get what changed in a field over time, read from its owner's eVault.
        Args:
            field_id (str): UUID of the field.
        Returns:
            Response data.
        """
        return self._get("eid/field-history", params={"fieldId": field_id})

    def eid_sync_field(self, field_id):
        """
        Push one field (and its cultivations) to its owner's eVault now.
        Args:
            field_id (str): UUID of the field.
        Returns:
            dict: Response data.
        """
        return self._post("eid/sync-field", {"fieldId": field_id})

    def eid_sync_layers(self, field_id):
        """
        Write every layer of a field into the authenticated user's eVault as MapLayers.
        Args:
            field_id (str): UUID of the field.
        Returns:
            dict: Response data.
        """
        return self._post("eid/sync-layers", {"fieldId": field_id})

    # ── Project / organisation eVaults ───────────────────────────────────────

    def eid_project_ename(self, project_id):
        """
        Get the eName of the eVault a project is connected to, or None.
        Args:
            project_id (str): UUID of the project.
        Returns:
            Response data.
        """
        return self._get("eid/project-ename", params={"projectId": project_id})

    def eid_project_ename_set(self, project_id, ename):
        """
        Connect a project to its eVault, or disconnect it with ename=None.
        Project owners only.
        Args:
            project_id (str): UUID of the project.
            ename (str or None): eName of the eVault, e.g. '@1d6887a5-...'.
        Returns:
            dict: Response data.
        """
        return self._put("eid/project-ename", {"projectId": project_id, "ename": ename})

    def eid_project_vault_status(self, project_id):
        """
        Get whether a project's connection to its eVault works.
        Args:
            project_id (str): UUID of the project.
        Returns:
            dict: Response data.
        """
        return self._get("eid/project-vault-status", params={"projectId": project_id})

    def eid_project_vault_retry(self, project_id):
        """
        Retry sharing the project's fields with its eVault and adding its
        members. Runs in the background; check eid_project_vault_status().
        Args:
            project_id (str): UUID of the project.
        Returns:
            dict: Response data.
        """
        return self._post("eid/project-vault-retry", {"projectId": project_id})

    def eid_environment_ename_set(self, environment_id, ename):
        """
        Connect an organisation (environment) to its eVault, or disconnect it
        with ename=None.
        Args:
            environment_id (str): UUID of the environment.
            ename (str or None): eName of the eVault.
        Returns:
            dict: Response data.
        """
        return self._put("eid/environment-ename", {"environmentId": environment_id, "ename": ename})
