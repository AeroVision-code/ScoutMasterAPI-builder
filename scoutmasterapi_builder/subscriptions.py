class Subscriptions:
    def subscriptions_by_field(self, field_id):
        """
        Get all the subscriptions which are related to a certain field
        Args:
            field_id (str): The ID of the field
        Returns:
            pd.DataFrame or list: DataFrame or JSON list with the relevant data
        """
        endpoint = f"subscription/{field_id}/"
        params = {}
        if self.output_format in ["geojson", "gdf"]:
            params["output"] = "geojson"

        # Pass params to _get
        data = self._get(endpoint, params=params)
        return self._format_output(data)