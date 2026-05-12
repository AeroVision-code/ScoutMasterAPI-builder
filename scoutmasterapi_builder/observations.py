import pandas as pd
import requests


class Observations:
    def observations(self, project_id):
        """
        Get all observations relevant for the given project
        Args:
            project_id (str): The ID of the project
        Returns:
            pd.DataFrame or list: DataFrame or JSON list with all data and 
            metadata pertaining to the observations.
        """
        endpoint = f"projects/{project_id}/observations"
        params = {}
        if self.output_format in ["geojson", "gdf"]:
            params["output"] = "geojson"

        # Pass params to _get
        data = self._get(endpoint, params=params)
        return self._format_output(data)
    
    def observation_by_id(self, observation_id):
        """
        Get all data and metadata for the given observation
        Args:
            observation_id (str): The ID of the observation
        Returns:
            pd.DataFrame or list: DataFrame or JSON list with all data and 
            metadata pertaining to the observation.
        """        
        endpoint = f"observations/{observation_id}"
        params = {}
        if self.output_format in ["geojson", "gdf"]:
            params["output"] = "geojson"

        # Pass params to _get
        data = self._get(endpoint, params=params)
        return self._format_output(data)
    
    def observation_values(self, observation_id):
        """
        Get the values that make up the given observation
        Args:
            observation_id (str): The ID of the observation
        Returns:
            pd.DataFrame or list: DataFrame or JSON list with all data 
            pertaining to the observation.
        """        
        endpoint = f"observations/{observation_id}/values"
        params = {}
        if self.output_format in ["geojson", "gdf"]:
            params["output"] = "geojson"
            
        # Pass params to _get
        data = self._get(endpoint, params=params)
        return self._format_output(data)

    def observations_create(self, project_id, obs_data):
        """
        Create a new observation in the specified project.

        Args:
            project_id (str): The ID of the project.
            obs_data (dict): Observation data with required fields:
                {
                    "user_id": "uuid",
                    "acquired_at": "ISO timestamp",
                    "geometry": { "type": "Point", "coordinates": [x, y] },
                    "reference_code": "string"
                }

        Returns:
            pd.DataFrame or dict: Created observation.
        """
        self._check_auth()
        
        endpoint = f"{self.host}projects/{project_id}/observations"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        try:
            # IMPORTANT: use json=obs_data
            response = requests.post(endpoint, json=obs_data, headers=headers)
            print(response)
            data = response.json()
          

            if response.status_code in (200, 201):
                self.output_format = "json"
                return self._format_output(data["data"][0])
                # return (
                #     pd.DataFrame([response_json])
                #     if self.output_format == "df"
                #     else response_json
                # )
            else:
                raise Exception(
                    f"Failed to create observation: "
                    f"{response.status_code} {response.text}"
                )

        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")
        
    def observations_values_create(self, obs_id, obs_data):
        """
        Create a new observation value.

        Args:
            obs_id (str): Observation ID.
            obs_data (dict): Value data, e.g.:
                {
                    "parameter_id": 1,
                    "value": 23.5,
                    "operator": ">",   # optional, default "="
                    "target_min": 20.0, # optional
                    "target_max": 30.0  # optional
                }

            Allowed operator symbols:
                =   equal to (default)
                !=  not equal to
                <   less than
                <=  less than or equal to
                >   greater than
                >=  greater than or equal to

        Returns:
            dict or DataFrame: Created value.
        """
        endpoint = f"observations/{obs_id}/values"

        # Optional: light client-side validation
        allowed_operators = {"=", "!=", "<", "<=", ">", ">="}
        operator = obs_data.get("operator", "=")
        if operator not in allowed_operators:
            raise ValueError(
                f"Invalid operator '{operator}'. Allowed: {sorted(allowed_operators)}"
            )
        obs_data["operator"] = operator
        # Optional: ensure target_min and target_max are floats or None
        self._validate_numeric_fields(obs_data, ["target_min", "target_max", "value"])
        try:
            data = self._post(endpoint, obs_data)
            return pd.DataFrame(data) if self.output_format == "df" else data
        except Exception as e:
            # Check if this is a 409 Conflict from the API
            msg = str(e)
            if "409" in msg:
                # Optional: parse JSON error
                try:
                    import json
                    error_info = json.loads(msg.split(" ", 1)[1])
                    return {
                        "status": "exists",
                        "message": error_info.get("error", "Value already exists"),
                        "fields": error_info.get("fields", [])
                    }
                except Exception:
                    return {"status": "exists", "message": "Observation value already exists."}
            # re-raise other exceptions
            raise

    def field_observations(self, field_id, page=None, limit=None, order=None,
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

    def observation_update(self, observation_id, reference_code=None, geometry=None,
                           observed_at=None, research_category_id=None):
        """
        Update an observation.
        Args:
            observation_id (str): UUID of the observation.
            reference_code (str, optional): New reference code.
            geometry (dict or str, optional): Updated geometry.
            observed_at (str, optional): ISO8601 observation timestamp.
            research_category_id (int or None, optional): Research category ID.
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
        endpoint = f"observations/{observation_id}"
        self._delete(endpoint)

