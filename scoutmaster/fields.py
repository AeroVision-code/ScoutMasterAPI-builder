import pandas as pd
import requests


class Fields:
    def fields(self, project_id):
        endpoint = f"projects/{project_id}/fields"
        params = {}
        if self.output_format in ["geojson", "gdf"]:
            params["output"] = "geojson"
        data = self._get(endpoint, params=params)
        return self._format_output(data)

    def field_by_id(self, field_id):
        endpoint = f"fields/{field_id}"
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
            project_id (str): UUID of the project.
            field_data (dict): Must include user_id, name, and geometry.
                geometry can be a GeoJSON Polygon dict or WKT string.

        Returns:
            DataFrame or dict: Created field.
        """
        endpoint = f"projects/{project_id}/fields"
        try:
            data = self._post(endpoint, field_data)
            return pd.DataFrame(data) if self.output_format == "df" else data
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")

    def fields_by_location(self, project_id, lat, long):
        """
        Find fields in a project that contain a given coordinate.

        Args:
            project_id (str): UUID of the project.
            lat (float): Latitude.
            long (float): Longitude.

        Returns:
            list or DataFrame: Fields containing the point.
        """
        endpoint = f"projects/{project_id}/fields/by-location"
        params = {"lat": lat, "long": long}
        data = self._get(endpoint, params=params)
        return self._format_output(data)

    def field_update(self, field_id, name=None, geometry=None):
        """
        Update a field's name and/or geometry.

        Args:
            field_id (str): UUID of the field.
            name (str, optional): New field name.
            geometry (dict or str, optional): New geometry as GeoJSON dict or WKT string.

        Returns:
            dict: Updated field data with message.
        """
        endpoint = f"fields/{field_id}"
        payload = {}
        if name is not None:
            payload["name"] = name
        if geometry is not None:
            payload["geometry"] = geometry
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
