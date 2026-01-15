class Cultivations:
    def cultivations(self, project_id):
        endpoint = f"projects/{project_id}/cultivations"
        params = {}
        if self.output_format in ["geojson", "gdf"]:
            params["output"] = "geojson"

        # Pass params to _get
        data = self._get(endpoint, params=params)
        return self._format_output(data)
    
    def cultivations_by_field(self, field_id):
        endpoint = f"fields/{field_id}/calendar"
        params = {}
        if self.output_format in ["geojson", "gdf"]:
            params["output"] = "geojson"

        # Pass params to _get
        data = self._get(endpoint, params=params)
        return self._format_output(data)

    def cultivations_create(self, field_id, cultivation_data):
        endpoint = f"fields/{field_id}/calendar"
        data = self._post(endpoint, cultivation_data)
        return self._format_output(data)
    