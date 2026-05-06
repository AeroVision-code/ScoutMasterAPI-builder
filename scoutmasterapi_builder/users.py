class Users:    
    def users(self, project_id):
        """
        Get all users who have access to the project.
        Args:
            project_id (str): The ID of the project
        Returns:
            pd.DataFrame or list: Users as DataFrame or JSON list.
        """
        endpoint = f"projects/{project_id}/users"
        params = {}
        if self.output_format in ["geojson", "gdf"]:
            params["output"] = "geojson"

        # Pass params to _get
        data = self._get(endpoint, params=params)
        return self._format_output(data)