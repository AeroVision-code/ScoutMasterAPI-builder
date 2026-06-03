import pandas as pd


class Observations:
    def observations(self, project_id, page=None, limit=None, order=None,
                     lang=None, sort_by=None, crs=None, output_format=None):
        """
        Get all observations for the given project.
        Args:
            project_id (str): The ID of the project.
            page (int, optional): Page number.
            limit (int, optional): Results per page.
            order (str, optional): 'asc' or 'desc'.
            lang (str, optional): Language code.
            sort_by (str, optional): Column to sort by.
            crs (int, optional): Target CRS EPSG code (default 4326).
            output_format (str, optional): 'wkt' or 'geojson'.
        Returns:
            pd.DataFrame or list: Observations as DataFrame or JSON list.
        """
        endpoint = f"projects/{project_id}/observations"
        params = {}
        if page: params["page"] = page
        if limit: params["limit"] = limit
        if order: params["order"] = order
        if lang: params["lang"] = lang
        if sort_by: params["sort_by"] = sort_by
        if crs: params["crs"] = crs
        if output_format:
            params["output_format"] = output_format
        elif self.output_format in ("geojson", "gdf"):
            params["output_format"] = "geojson"
        data = self._get(endpoint, params=params)
        return self._format_output(data)

    def observations_by_field(self, field_id, page=None, limit=None, order=None,
                               lang=None, sort_by=None, crs=None, output_format=None):
        """
        Get all observations for a field.
        Args:
            field_id (str): UUID of the field.
            page (int, optional): Page number.
            limit (int, optional): Results per page.
            order (str, optional): 'asc' or 'desc'.
            lang (str, optional): Language code.
            sort_by (str, optional): Column to sort by.
            crs (int, optional): Target CRS EPSG code (default 4326).
            output_format (str, optional): 'wkt' or 'geojson'.
        Returns:
            DataFrame, GeoDataFrame, or dict.
        """
        endpoint = f"fields/{field_id}/observations"
        params = {}
        if page: params["page"] = page
        if limit: params["limit"] = limit
        if order: params["order"] = order
        if lang: params["lang"] = lang
        if sort_by: params["sort_by"] = sort_by
        if crs: params["crs"] = crs
        if output_format:
            params["output_format"] = output_format
        elif self.output_format in ("geojson", "gdf"):
            params["output_format"] = "geojson"
        data = self._get(endpoint, params=params)
        return self._format_output(data)

    # Legacy alias
    def field_observations(self, field_id, **kwargs):
        """Deprecated: use observations_by_field() instead."""
        return self.observations_by_field(field_id, **kwargs)

    def observation_by_id(self, observation_id, crs=None, output_format=None):
        """
        Get all data and metadata for the given observation.
        Args:
            observation_id (str): The ID of the observation.
            crs (int, optional): Target CRS EPSG code (default 4326).
            output_format (str, optional): 'wkt' or 'geojson'.
        Returns:
            pd.DataFrame or list: Observation as DataFrame or JSON.
        """
        endpoint = f"observations/{observation_id}"
        params = {}
        if crs: params["crs"] = crs
        if output_format:
            params["output_format"] = output_format
        elif self.output_format in ("geojson", "gdf"):
            params["output_format"] = "geojson"
        data = self._get(endpoint, params=params)
        return self._format_output(data)

    def observation_create(self, project_id, user_id, reference_code, acquired_at,
                           geometry, reported_at=None, research_category_id=None):
        """
        Create a new observation in a project.
        Args:
            project_id (str): UUID of the project.
            user_id (str): UUID of the user creating the observation.
            reference_code (str): Reference code for the observation.
            acquired_at (str): ISO8601 acquisition timestamp.
            geometry (dict or str): GeoJSON Point dict or WKT string.
                e.g. {"type": "Point", "coordinates": [5.1234, 52.5678]}
            reported_at (str, optional): ISO8601 reported timestamp.
            research_category_id (int, optional): Research category ID.
        Returns:
            dict: Created observation data.
        """
        payload = {
            "user_id": user_id,
            "reference_code": reference_code,
            "acquired_at": acquired_at,
            "geometry": geometry,
        }
        if reported_at: payload["reported_at"] = reported_at
        if research_category_id is not None: payload["research_category_id"] = research_category_id
        data = self._post(f"projects/{project_id}/observations", payload)
        return data

    # Legacy alias
    def observations_create(self, project_id, obs_data):
        """Deprecated: use observation_create() instead."""
        return self.observation_create(
            project_id,
            user_id=obs_data.get("user_id"),
            reference_code=obs_data.get("reference_code"),
            acquired_at=obs_data.get("acquired_at"),
            geometry=obs_data.get("geometry"),
            reported_at=obs_data.get("reported_at"),
            research_category_id=obs_data.get("research_category_id"),
        )

    def observation_update(self, observation_id, reference_code=None, geometry=None,
                           observed_at=None, research_category_id=None):
        """
        Update an observation.
        Args:
            observation_id (str): UUID of the observation.
            reference_code (str, optional): New reference code.
            geometry (dict or str, optional): Updated geometry.
            observed_at (str, optional): ISO8601 observation timestamp.
            research_category_id (int or None, optional): Research category ID (pass None to clear).
        Returns:
            dict: Updated observation data.
        """
        endpoint = f"observations/{observation_id}"
        payload = {}
        if reference_code is not None: payload["reference_code"] = reference_code
        if geometry is not None: payload["geometry"] = geometry
        if observed_at is not None: payload["observed_at"] = observed_at
        if research_category_id is not None: payload["research_category_id"] = research_category_id
        data = self._patch(endpoint, payload)
        return data

    def observation_delete(self, observation_id):
        """
        Delete an observation by ID.
        Args:
            observation_id (str): UUID of the observation.
        Returns:
            None (204 No Content).
        """
        self._delete(f"observations/{observation_id}")

    def observation_values(self, observation_id):
        """
        Get the measurement values for the given observation.
        Args:
            observation_id (str): The ID of the observation.
        Returns:
            pd.DataFrame or list: Observation values.
        """
        data = self._get(f"observations/{observation_id}/values")
        return self._format_output(data)

    def observation_value_create(self, observation_id, parameter_id, value,
                                  operator=None, target_min=None, target_max=None):
        """
        Add a measurement value to an observation.
        Args:
            observation_id (str): UUID of the observation.
            parameter_id (int): Observation parameter ID.
            value (float): Measured value.
            operator (str, optional): Comparison operator (=, !=, <, <=, >, >=).
            target_min (float, optional): Target minimum value.
            target_max (float, optional): Target maximum value.
        Returns:
            dict: Created observation value.
        """
        allowed_operators = {"=", "!=", "<", "<=", ">", ">="}
        if operator and operator not in allowed_operators:
            raise ValueError(f"Invalid operator '{operator}'. Allowed: {sorted(allowed_operators)}")
        payload = {"parameter_id": parameter_id, "value": float(value)}
        if operator: payload["operator"] = operator
        if target_min is not None: payload["target_min"] = float(target_min)
        if target_max is not None: payload["target_max"] = float(target_max)
        data = self._post(f"observations/{observation_id}/values", payload)
        return data

    # Legacy alias
    def observations_values_create(self, obs_id, obs_data):
        """Deprecated: use observation_value_create() instead."""
        return self.observation_value_create(
            obs_id,
            parameter_id=obs_data["parameter_id"],
            value=obs_data["value"],
            operator=obs_data.get("operator"),
            target_min=obs_data.get("target_min"),
            target_max=obs_data.get("target_max"),
        )
