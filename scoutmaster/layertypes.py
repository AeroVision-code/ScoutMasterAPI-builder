class LayerTypes:
    def project_layer_types(self, project_id, page=None, limit=None, order=None,
                            lang=None, sort_by=None, layer_sensor_id=None):
        """
        Get layer types available for a project.

        Args:
            project_id (str): UUID of the project.
            page (int, optional): Page number (default 1).
            limit (int, optional): Results per page.
            order (str, optional): 'asc' or 'desc'.
            lang (str, optional): Language code.
            sort_by (str, optional): 'name', 'created_at', or 'updated_at'.
            layer_sensor_id (str, optional): Filter by sensor ID.

        Returns:
            DataFrame or dict: Paginated layer types.
        """
        endpoint = f"projects/{project_id}/layer-types"
        params = {}
        if page:
            params["page"] = page
        if limit:
            params["limit"] = limit
        if order:
            params["order"] = order
        if lang:
            params["lang"] = lang
        if sort_by:
            params["sort_by"] = sort_by
        if layer_sensor_id:
            params["layer_sensor_id"] = layer_sensor_id
        data = self._get(endpoint, params=params)
        return self._format_output(data)

    def field_layer_types(self, field_id, page=None, limit=None, order=None,
                          lang=None, sort_by=None, layer_sensor_id=None):
        """
        Get layer types available for a specific field.

        Args:
            field_id (str): UUID of the field.
            page (int, optional): Page number (default 1).
            limit (int, optional): Results per page.
            order (str, optional): 'asc' or 'desc'.
            lang (str, optional): Language code.
            sort_by (str, optional): 'name', 'created_at', or 'updated_at'.
            layer_sensor_id (str, optional): Filter by sensor ID.

        Returns:
            DataFrame or dict: Paginated layer types.
        """
        endpoint = f"fields/{field_id}/layer-types"
        params = {}
        if page:
            params["page"] = page
        if limit:
            params["limit"] = limit
        if order:
            params["order"] = order
        if lang:
            params["lang"] = lang
        if sort_by:
            params["sort_by"] = sort_by
        if layer_sensor_id:
            params["layer_sensor_id"] = layer_sensor_id
        data = self._get(endpoint, params=params)
        return self._format_output(data)

    def layer_type_colormap(self, layer_type_id):
        """
        Get the colormap entries for a layer type.

        Args:
            layer_type_id (str): UUID of the layer type.

        Returns:
            list or DataFrame: Colormap color strings.
        """
        endpoint = f"layer-types/{layer_type_id}/colormap"
        data = self._get(endpoint)
        return self._format_output(data)

    def layer_types(self, project_id=None):
        """Alias for project_layer_types. Prefer calling project_layer_types() directly."""
        if project_id is None:
            raise ValueError(
                "project_id is required. Use project_layer_types(project_id) or field_layer_types(field_id)."
            )
        return self.project_layer_types(project_id)
