import pandas as pd
import requests


class Fields:
    def fields(self, project_id):
        """
        Get all the fields that are used within the specified project.
        Args:
            project_id (str): The ID of the project
        Returns:
            pd.DataFrame or list: Fields as DataFrame or JSON list.
        """
        endpoint = f"projects/{project_id}/fields"
        params = {}
        if self.output_format in ["geojson", "gdf"]:
            params["output"] = "geojson"

        # Pass params to _get
        data = self._get(endpoint, params=params)
        return self._format_output(data)
    
    def field_by_id(self, field_id):
        """
        Get the field indicated by the given field ID.
        Args:
            field_id (str): The ID of the field
        Returns:
            pd.DataFrame or list: Field as DataFrame or JSON list.
        """
        endpoint = f"fields/{field_id}"
        params = {}
        if self.output_format in ["geojson", "gdf"]:
            params["output"] = "geojson"
        data = self._get(endpoint, params=params)
        if self.output_format in ["df"]:
            data = [data]
        return self._format_output(data)
    
    def field_by_location(self, project_id, lat, lon):
        """
        Get the field used within the specified project, filtered by the point location.
        Args:
            project_id (str): The ID of the project
            lat (float): the latitude of the point
            lon (float): the longitude of the point
        Returns:
            pd.DataFrame or list: Field as DataFrame or JSON list.
        """
        endpoint = f"projects/{project_id}/fields"
        endpoint += f"/by-location?lat={lat}&long={lon}"
        params = {}
        if self.output_format in ["geojson", "gdf"]:
            params["output"] = "geojson"
        data = self._get(endpoint, params=params)
        if self.output_format in ["df"]:
            data = [data]
        return self._format_output(data)
        
    def fields_create(self, project_id, field_data):
        """
        Create a new field in the specified project.
        Args:
            project_id (str): The ID of the project.
            field_data (dict): Field data with required fields:
                {
                    "user_id": "uuid",
                    "name": "string",
                    "properties": {
                        "description": "string"
                    },
                    "geometry": { "type": "Polygon", "coordinates": [[x, y]] },
                }
        Returns:
            pd.DataFrame or dict: Created field.
        """
        endpoint = f"projects/{project_id}/fields"
        try:
            data = self._post(endpoint, field_data)
            return pd.DataFrame(data) if self.output_format == "df" else data

        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")

    def field_update(self, field_id, name=None, geometry=None):
        """
        Update a field name and/or geometry.
        Args:
            field_id (str): UUID of the field.
            name (str, optional): New field name.
            geometry (dict or str, optional): New geometry as GeoJSON dict or WKT string.
        Returns:
            dict: Updated field data with message.
        """
        endpoint = f"fields/{field_id}"
        payload = {}
        if name is not None: payload["name"] = name
        if geometry is not None: payload["geometry"] = geometry
        data = self._patch(endpoint, payload)
        return data

    def field_delete(self, field_id):
        """
        Delete a field by ID.
        Args:
            field_id (str): UUID of the field.
        Returns:
            dict: Deleted field data with message.
        """
        endpoint = f"fields/{field_id}"
        data = self._delete(endpoint)
        return data

