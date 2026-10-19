EXCLUSION_REASONS = ("cloud_cover", "bad_quality", "duplicate", "other")


class LayerExclusions:
    """Excluded layers are left out of a field's timeseries but are otherwise normal layers."""

    def _check_reason(self, reason):
        if reason not in EXCLUSION_REASONS:
            raise ValueError(f"reason must be one of {EXCLUSION_REASONS}")

    def field_layer_exclusions(self, field_id):
        """
        Get the excluded layers of a field.
        Args:
            field_id (str): UUID of the field.
        Returns:
            pd.DataFrame or list: Layer exclusions.
        """
        endpoint = f"fields/{field_id}/layers/exclusions"
        data = self._get(endpoint)
        return self._format_output(data)

    def project_layer_exclusions(self, project_id):
        """
        Get the excluded layers across all fields of a project.
        Args:
            project_id (str): UUID of the project.
        Returns:
            pd.DataFrame or list: Layer exclusions.
        """
        endpoint = f"projects/{project_id}/layers/exclusions"
        data = self._get(endpoint)
        return self._format_output(data)

    def layer_exclude(self, layer_id, reason, note=None):
        """
        Exclude a layer from the field's timeseries, or replace the reason/note
        of an existing exclusion. The timeseries is rebuilt in the background.
        Args:
            layer_id (int): ID of the layer.
            reason (str): 'cloud_cover', 'bad_quality', 'duplicate' or 'other'.
            note (str, optional): Free-text explanation.
        Returns:
            dict: The layer exclusion.
        """
        self._check_reason(reason)
        endpoint = f"layers/{layer_id}/exclusion"
        payload = {"reason": reason}
        if note is not None: payload["note"] = note
        data = self._put(endpoint, payload)
        return data

    def layer_include(self, layer_id):
        """
        Include a previously excluded layer again. No-op if it isn't excluded.
        Args:
            layer_id (int): ID of the layer.
        Returns:
            bool: True on success (204 No Content).
        """
        endpoint = f"layers/{layer_id}/exclusion"
        return self._delete(endpoint)

    def field_layers_exclude(self, field_id, layer_ids, reason, note=None):
        """
        Exclude several layers of a field at once. All layers must belong to
        the field, otherwise nothing is changed.
        Args:
            field_id (str): UUID of the field.
            layer_ids (list[int]): IDs of the layers to exclude.
            reason (str): 'cloud_cover', 'bad_quality', 'duplicate' or 'other'.
            note (str, optional): Free-text explanation.
        Returns:
            list: The layer exclusions.
        """
        self._check_reason(reason)
        endpoint = f"fields/{field_id}/layers/exclusions"
        payload = {"layer_ids": list(layer_ids), "reason": reason}
        if note is not None: payload["note"] = note
        data = self._post(endpoint, payload)
        return data

    def field_layers_include(self, field_id, layer_ids):
        """
        Include several layers of a field again. All layers must belong to the
        field, otherwise nothing is changed.
        Args:
            field_id (str): UUID of the field.
            layer_ids (list[int]): IDs of the layers to include again.
        Returns:
            dict: Empty on success (204 No Content).
        """
        endpoint = f"fields/{field_id}/layers/inclusions"
        data = self._post(endpoint, {"layer_ids": list(layer_ids)})
        return data
