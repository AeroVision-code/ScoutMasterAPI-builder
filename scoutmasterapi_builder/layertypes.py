class LayerTypes:
    def layer_types(self, project_id=None, page=None, limit=None, order=None,
                    lang=None, sort_by=None):

        """
        Retrieves the layer types available to a project.
        Args:
            project_id (str): The ID of the project.
            page (int, optional): Page number (default 1).
            limit (int, optional): Results per page. Omit to return all.
            order (str, optional): 'asc' or 'desc'.
            lang (str, optional): Language for field labels.
            sort_by (str, optional): 'name' or 'group_name'.
        Returns:
            pd.DataFrame or list: Layer types as DataFrame or JSON list.
        """
        endpoint = f"projects/{project_id}/layer-types"
        params = {}
        if page: params["page"] = page
        if limit: params["limit"] = limit
        if order: params["order"] = order
        if lang: params["lang"] = lang
        if sort_by: params["sort_by"] = sort_by
        data = self._get(endpoint, params=params)
        return self._format_output(data)

    def layer_types_by_fieldid(self, field_id, page=None, limit=None, order=None,
                               lang=None, sort_by=None):
        """
        Retrieves the layer types available for a field.
        Args:
            field_id (str): UUID of the field.
            page (int, optional): Page number (default 1).
            limit (int, optional): Results per page. Omit to return all.
            order (str, optional): 'asc' or 'desc'.
            lang (str, optional): Language for field labels.
            sort_by (str, optional): 'name' or 'group_name'.
        Returns:
            pd.DataFrame or list: Layer types as DataFrame or JSON list.
        """
        endpoint = f"fields/{field_id}/layer-types"
        params = {}
        if page: params["page"] = page
        if limit: params["limit"] = limit
        if order: params["order"] = order
        if lang: params["lang"] = lang
        if sort_by: params["sort_by"] = sort_by
        data = self._get(endpoint, params=params)
        return self._format_output(data)

    def layer_type_by_id(self, layer_type_id, lang=None):
        """
        Retrieves a single layer type by id.
        Args:
            layer_type_id (str): UUID of the layer type.
            lang (str, optional): Language for labels.
        Returns:
            dict: The layer type record.
        """
        endpoint = f"layer-types/{layer_type_id}"
        params = {}
        if lang: params["lang"] = lang
        data = self._get(endpoint, params=params)
        return data

    def layer_type_colormap(self, layer_type_id):
        """
        Retrieves the colormap associated with a layer type
        Args:
            layer_type_id (str, required)
        Returns:
            colormap
        """
        endpoint = f"layer-types/{layer_type_id}/colormap"
        data = self._get(endpoint)
        return data
        
        
        
        