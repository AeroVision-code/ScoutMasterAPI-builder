class LayerTypes:
    def layer_types(self, project_id=None):

        """
        Retrieves available layer types, optionally filtered by layer source.
        Args:
            layer_source_id (str, optional): Filter by layer source ID.
        Returns:
            pd.DataFrame or list: Layer types as DataFrame or JSON list.
        """
        endpoint = f"projects/{project_id}/layer-types"
        params = {}
        if project_id is not None:
            params["project_id"] = project_id
        data = self._get(endpoint, params)
        return self._format_output(data)
    
    def layer_types_by_fieldid(self, field_id):
        """
        Retrieves available layer types, filtered for field
        Args: 
            layer_id (str, required)
        Returns:
            pd.DataFrame or list: Layer types as DataFrame or JSON list.
        """
        endpoint = f"fields/{field_id}/layer-types"
        data = self._get(endpoint)
        return self._format_output(data)
    
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
        
        
        
        