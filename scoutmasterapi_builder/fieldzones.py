ZONE_TYPES = (1, 2, 3, 4)


class FieldZones:
    def field_zones(self, field_id, page=None, limit=None, order=None, lang=None,
                    search=None, sort_by=None, crs=None):
        """
        Get all field zones of a field.
        Args:
            field_id (str): UUID of the field.
            page (int, optional): Page number (default 1).
            limit (int, optional): Results per page. Omit to return all.
            order (str, optional): 'asc' or 'desc'.
            lang (str, optional): Language for labels ('en', 'nl', 'de', 'fr').
            search (str, optional): Case-insensitive match on zone name or id.
            sort_by (str, optional): 'name', 'created_at' or 'updated_at'.
            crs (int, optional): Output CRS EPSG code (default 4326).
        Returns:
            pd.DataFrame, GeoDataFrame, dict or GeoJSON depending on
            output_format / spatial.
        """
        endpoint = f"fields/{field_id}/zones"
        params = {}
        if page: params["page"] = page
        if limit: params["limit"] = limit
        if order: params["order"] = order
        if lang: params["lang"] = lang
        if search: params["search"] = search
        if sort_by: params["sort_by"] = sort_by
        if crs: params["crs"] = crs
        data = self._get_paged(endpoint, params=params)
        return self._format_output(data)

    def field_zone_by_id(self, zone_id, lang=None, crs=None):
        """
        Get a single field zone by id.
        Args:
            zone_id (str): UUID of the field zone.
            lang (str, optional): Language for labels.
            crs (int, optional): Output CRS EPSG code (default 4326).
        Returns:
            pd.DataFrame, GeoDataFrame, dict or GeoJSON depending on
            output_format / spatial.
        """
        endpoint = f"field-zones/{zone_id}"
        params = {}
        if lang: params["lang"] = lang
        if crs: params["crs"] = crs
        data = self._get(endpoint, params=params)
        return self._format_output(data)

    def field_zone_create(self, field_id, zone_type, geometry, name=None,
                          definitief=None, properties=None):
        """
        Create a field zone. The geometry must be a Polygon (WGS84) that lies
        within the field boundary.
        Args:
            field_id (str): UUID of the field.
            zone_type (int): Zone type, one of 1, 2, 3, 4.
            geometry (dict or str): GeoJSON Polygon dict or WKT string.
            name (str, optional): Zone name.
            definitief (bool, optional): True = confirmed zone, False = concept
                (server default False).
            properties (dict, optional): Free-form properties.
        Returns:
            dict: Created field zone.
        """
        if zone_type not in ZONE_TYPES:
            raise ValueError(f"zone_type must be one of {ZONE_TYPES}")
        endpoint = f"fields/{field_id}/zones"
        payload = {"zone_type": zone_type, "geometry": geometry}
        if name is not None: payload["name"] = name
        if definitief is not None: payload["definitief"] = definitief
        if properties is not None: payload["properties"] = properties
        data = self._post(endpoint, payload)
        return data

    def field_zone_update(self, zone_id, name=None, geometry=None, zone_type=None,
                          definitief=None, properties=None, lang=None, crs=None):
        """
        Update a field zone. At least one field must be provided.
        Args:
            zone_id (str): UUID of the field zone.
            name (str, optional): New zone name.
            geometry (dict or str, optional): New Polygon as GeoJSON dict or WKT (WGS84).
            zone_type (int, optional): New zone type, one of 1, 2, 3, 4.
            definitief (bool, optional): True = confirmed zone, False = concept.
            properties (dict, optional): New free-form properties.
            lang (str, optional): Language for labels in the response.
            crs (int, optional): Output CRS EPSG code for the response geometry.
        Returns:
            dict: Updated field zone.
        """
        if zone_type is not None and zone_type not in ZONE_TYPES:
            raise ValueError(f"zone_type must be one of {ZONE_TYPES}")
        endpoint = f"field-zones/{zone_id}"
        payload = {}
        if name is not None: payload["name"] = name
        if geometry is not None: payload["geometry"] = geometry
        if zone_type is not None: payload["zone_type"] = zone_type
        if definitief is not None: payload["definitief"] = definitief
        if properties is not None: payload["properties"] = properties
        if not payload:
            raise ValueError("Provide at least one field to update")
        params = {}
        if lang: params["lang"] = lang
        if crs: params["crs"] = crs
        data = self._patch(endpoint, payload, params=params)
        return data

    def field_zone_delete(self, zone_id):
        """
        Delete a field zone by id.
        Args:
            zone_id (str): UUID of the field zone.
        Returns:
            bool: True if the zone was deleted (204 No Content).
        """
        endpoint = f"field-zones/{zone_id}"
        return self._delete(endpoint)

    # ── GeoJSON variants (not paginated; return a FeatureCollection) ─────────
    def field_zones_geojson(self, field_id, lang=None, sort_by=None, order=None, crs=None):
        """
        Get all field zones of a field as a GeoJSON FeatureCollection.
        Args:
            field_id (str): UUID of the field.
            lang (str, optional): Language for labels.
            sort_by (str, optional): 'name', 'created_at' or 'updated_at'.
            order (str, optional): 'asc' or 'desc'.
            crs (int, optional): Output CRS EPSG code (default 4326).
        Returns:
            GeoDataFrame, dict, or JSON depending on output_format.
        """
        endpoint = f"fields/{field_id}/zones/geojson"
        params = {}
        if lang: params["lang"] = lang
        if sort_by: params["sort_by"] = sort_by
        if order: params["order"] = order
        if crs: params["crs"] = crs
        data = self._get(endpoint, params=params)
        return self._format_output(data)

    def field_zone_by_id_geojson(self, zone_id, lang=None, crs=None):
        """
        Get a single field zone as a GeoJSON FeatureCollection.
        Args:
            zone_id (str): UUID of the field zone.
            lang (str, optional): Language for labels.
            crs (int, optional): Output CRS EPSG code (default 4326).
        Returns:
            GeoDataFrame, dict, or JSON depending on output_format.
        """
        endpoint = f"field-zones/{zone_id}/geojson"
        params = {}
        if lang: params["lang"] = lang
        if crs: params["crs"] = crs
        data = self._get(endpoint, params=params)
        return self._format_output(data)
