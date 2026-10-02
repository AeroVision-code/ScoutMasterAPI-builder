import pandas as pd
import requests

class FieldZones:
    def field_zones(self, field_id=None, page=None, limit=None, order=None,
                    lang=None, sort_by=None):
        """
        Retrieves the field zones located in a field.
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
        endpoint = f"/fields/{field_id}/zones"
        params = {}
        if page: params["page"] = page
        if limit: params["limit"] = limit
        if order: params["order"] = order
        if lang: params["lang"] = lang
        if sort_by: params["sort_by"] = sort_by
        data = self._get_paginated(endpoint, params=params, limit=limit, page=page)
        return self._format_output(data)

    def field_zone_by_id(self, zone_id, page=None, limit=None, order=None,
                               lang=None, sort_by=None):
        """
        Retrieves a filed zone by id.
        Args:
            zone_id (str): UUID of the field zone.
            page (int, optional): Page number (default 1).
            limit (int, optional): Results per page. Omit to return all.
            order (str, optional): 'asc' or 'desc'.
            lang (str, optional): Language for field labels.
            sort_by (str, optional): 'name' or 'group_name'.    
        Returns:
            pd.DataFrame or list: Field zone as DataFrame or JSON list.
        """
        endpoint = f"/fields/{field_id}/zones/geojson"
        params = {}
        if page: params["page"] = page
        if limit: params["limit"] = limit
        if order: params["order"] = order
        if lang: params["lang"] = lang
        if sort_by: params["sort_by"] = sort_by
        data = self._get(endpoint, params=params)
        return self._format_output(data)

"""

POST
/fields/{fieldId}/zones
Create a field zone
GET

Return all field zones of a field as GeoJSON
GET
/field-zones/{zoneId}
Return a field zone by id
DELETE
/field-zones/{zoneId}
Delete a field zone
PATCH
/field-zones/{zoneId}
Update a field zone
GET
/field-zones/{zoneId}/geojson
Return a field zone by id as GeoJSON

""""""
