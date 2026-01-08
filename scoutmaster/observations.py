import pandas as pd
import requests


class Observations:
    def observations(self, project_id):
        endpoint = f"projects/{project_id}/observations"
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
                    "operator": ">"   # optional, default "="
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
        self._check_auth()

        endpoint = f"{self.host}observations/{obs_id}/values"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        # Optional: light client-side validation
        allowed_operators = {"=", "!=", "<", "<=", ">", ">="}
        if "operator" in obs_data and obs_data["operator"] not in allowed_operators:
            raise ValueError(
                f"Invalid operator '{obs_data['operator']}'. "
                f"Allowed operators: {sorted(allowed_operators)}"
            )

        try:
            response = requests.post(endpoint, json=obs_data, headers=headers)

            data = response.json()

            if response.status_code in (200, 201):
                self.output_format = "json"
                return self._format_output(data)
            else:
                raise Exception(
                    f"Failed to create observation value: "
                    f"{response.status_code} {response.text}"
                )

        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")


        