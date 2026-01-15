import pandas as pd
import requests


class Fields:
    def fields(self, project_id):
        endpoint = f"projects/{project_id}/fields"
        params = {}
        if self.output_format in ["geojson", "gdf"]:
            params["output"] = "geojson"

        # Pass params to _get
        data = self._get(endpoint, params=params)
        return self._format_output(data)
    
    def fields_create(self, project_id, field_data):
        """
        Create a new observation in the specified project.

        Args:
            project_id (str): The ID of the project.
            obs_data (dict): Observation data with required fields:
                {
                    "user_id": "uuid",
                    "name": "string"
                    "properties": {
                        "des"
                    },
                    "geometry": { "type": "Polygon, "coordinates": [[x, y]] },
                    "reference_code": "string"
                }

        Returns:
            pd.DataFrame or dict: Created observation.
        """
      
        endpoint = f"projects/{project_id}/fields"
        try:
            data = self._post(endpoint, field_data)
            return pd.DataFrame(data) if self.output_format == "df" else data

        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")