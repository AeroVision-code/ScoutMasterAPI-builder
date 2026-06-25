import pandas as pd
import requests


class Fields:
    def fields(self, project_id, page=None, limit=None, order=None, lang=None, sort_by=None, crs=None):
        """
        Get all the fields that are used within the specified project.
        Args:
            project_id (str): The ID of the project
            page (int, optional): Page number (default 1).
            limit (int, optional): Results per page. Omit to return all.
            order (str, optional): 'asc' or 'desc'.
            lang (str, optional): Language for field labels.
            sort_by (str, optional): 'name', 'created_at' or 'updated_at'.
            crs (int, optional): Output CRS EPSG code (default 4326).
        Returns:
            pd.DataFrame or list: Fields as DataFrame or JSON list.
        """
        endpoint = f"projects/{project_id}/fields"
        params = {}
        if page: params["page"] = page
        if limit: params["limit"] = limit
        if order: params["order"] = order
        if lang: params["lang"] = lang
        if sort_by: params["sort_by"] = sort_by
        if crs: params["crs"] = crs
        # spatial shaping is done client-side from the WKT geometry the regular
        # endpoint returns, so pagination is preserved. Use fields_geojson() for
        # the server's GeoJSON FeatureCollection.
        data = self._get(endpoint, params=params)
        return self._format_output(data)

    def field_by_id(self, field_id):
        """
        Get the field indicated by the given field ID.
        Args:
            field_id (str): The ID of the field
        Returns:
            pd.DataFrame, GeoDataFrame, dict or GeoJSON depending on
            output_format / spatial.
        """
        endpoint = f"fields/{field_id}"
        data = self._get(endpoint)
        return self._format_output(data)

    def field_by_location(self, project_id, lat, lon):
        """
        Get the field used within the specified project, filtered by the point location.
        Args:
            project_id (str): The ID of the project
            lat (float): the latitude of the point
            lon (float): the longitude of the point
        Returns:
            pd.DataFrame, GeoDataFrame, dict or GeoJSON depending on
            output_format / spatial.
        """
        # No GeoJSON variant for by-location; the regular response carries WKT
        # geometry which _format_output parses when spatial is set.
        endpoint = f"projects/{project_id}/fields/by-location"
        params = {"lat": lat, "long": lon}
        data = self._get(endpoint, params=params)
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
            return self._format_output(data)

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
            bool: True if the field was deleted successfully (204 No Content).
        """
        endpoint = f"fields/{field_id}"
        deleted = self._delete(endpoint)
        if deleted:
            print(f" > Field \033[94m{field_id}\033[0m deleted successfully.")
        return deleted

