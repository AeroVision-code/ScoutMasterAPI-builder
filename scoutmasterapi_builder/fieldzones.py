import requests

class FieldZones:
    def field_zones(self, field_id=None, page=None, limit=None, order=None,
                    lang=None, sort_by=None):
        """
        Retrieves the field zones found in a field.
        Args:
            field_id (str): The ID of the field.
            page (int, optional): Page number (default 1).
            limit (int, optional): Results per page. Omit to return all.
            order (str, optional): 'asc' or 'desc'.
            lang (str, optional): Language for field labels.
            sort_by (str, optional): 'name' or 'group_name'.
        Returns:
            pd.DataFrame or list: Fields as DataFrame or JSON list.

        """
        endpoint = f"fields/{field_id}/zones"
        params = {}
        if page: params["page"] = page
        if limit: params["limit"] = limit
        if order: params["order"] = order
        if lang: params["lang"] = lang
        if sort_by: params["sort_by"] = sort_by
        data = self._get(endpoint, params=params)
        return self._format_output(data)

    def field_zone_by_id(self, zone_id, page=None, limit=None, order=None,
                               lang=None, sort_by=None):
        """
        Retrieves a field zone by id.
        Args:
            zone_id (str): UUID of the field zone.
            lang (str, optional): Language for field labels.    
        Returns:
            pd.DataFrame or list: Field zone as DataFrame or JSON list.
        """
        endpoint = f"field-zones/{zone_id}"
        params = {}
        if lang: params["lang"] = lang
        data = self._get(endpoint, params=params)
        return self._format_output([data])

    def field_zone_create(self, field_id, field_zone_data):
        """
        Create a new field zone in the specified field (post).
        Args: 
            field_id (str): UUID of the field.
            field_zone_data (dict): Field zone data with required fields:
            {
                "user_id": "uuid",
                "name": "string",
                "properties": {
                    "additionalProp1": "string" (etcetera)
                },
                "geometry": { "type": "Polygon", "coordinates": [[x, y]] },
            }
        Returns
             pd.DataFrame or dict: Created field zone.
        """
        endpoint = f"field-zones/{field_id}/zones"
        try:
            data = self._post(endpoint, field_zone_data)
            return self._format_output(data)

        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")

    def field_zones_as_geojson(self, field_id):
        """
        Returns the field zones found in a field as GeoJSON.
        Args:
            field_id (str): The ID of the field.
        Returns: 
            GeoJSON 
        """
        endpoint = f"fields/{field_id}/zones/geojson"
        result = self._get(endpoint)
        return result

    def field_zone_as_geojson(self, zone_id):
        """
        Returns the field zone by id as GeoJSON 
        Args:
           zone_id (str): The ID of the field zone
        Returns:
            GeoJSON 
        """
        endpoint = f"field-zones/{zone_id}/geojson"
        result = self._get(endpoint)
        return result
        
    def field_zone_update(self, zone_id, field_zone_data):
        """
        Update a field zone, name, geometry, type or properties (patch)
        Args:
            zone_id (str): UUID of the field.
            field_zone_data (dict): Field zone data with one of the following fields:
                "name": "string",
                "zone_type": "int",
                "geometry": { "type": "Polygon", "coordinates": [[x, y]] },
                "properties": "dict"
                e.g. crop and variety as JSON.
        Returns:
            dict: Updated field zone data with message.
        """
        endpoint = f"field-zones/{zone_id}"
        data = self._patch(endpoint, field_zone_data)
        return data
        
    def field_zone_delete(self, zone_id):
        """
        Delete a field zone, name, geometry, type or properties (delete)
        Args: 
            zone_id (str): UUID of the field.
        Returns:
            bool: True if the field was deleted successfully (204 No Content).
        """
        endpoint = f"field-zones/{zone_id}"
        deleted = self._delete(endpoint)
        if deleted:
            print(f" > Field zone \033[94m{zone_id}\033[0m deleted successfully.")
        return deleted
