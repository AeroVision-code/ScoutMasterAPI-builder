import requests
import pandas as pd
from requests.auth import HTTPBasicAuth
import geopandas as gpd
from IPython.display import display, HTML

class ScoutMasterAPI:
    """
    ScoutmasterAPI provides an interface to interact with the ScoutMaster API v2.
    Attributes:
        token_url (str): The URL to obtain the OAuth2 access token.
        access_token (str): The OAuth2 access token for authenticated requests.
        version (str): The API version (default: "v2").
        host (str): The base URL for the API endpoints.
        output (str): The default output format ("df" for pandas DataFrame).
    Methods:
        __init__(token_url):
            Initializes the API client with the given token URL.
        authenticate(client_id, client_secret):
            Authenticates with the API using client credentials and retrieves an access token.
        crops(output="json"):
            Retrieves the list of crops. Returns data as JSON or pandas DataFrame.
        crop_rotations(field_id, output="df"):
            Retrieves crop rotation information for a specific field. Returns data as JSON or pandas DataFrame.
        fields(project_id, output="df"):
            Retrieves the list of fields for a given project. Returns data as JSON or pandas DataFrame.
        crop_varieties(crop_id, output="df"):
            Retrieves the list of crop varieties for a given crop. Returns data as JSON or pandas DataFrame.
        layers(field_id, layer_type_id=None, output="df"):
            Retrieves layers for a specific field, optionally filtered by layer type. Returns data as JSON or pandas DataFrame.
        layers_types(layer_source_id=None, output="df"):
            Retrieves available layer types, optionally filtered by layer source. Returns data as JSON or pandas DataFrame.
    Output options are "df" (pandas DataFrame) and "json".
    """
    def __init__(self):
        self.token_url = "https://eu-central-1fq4qt7w6q.auth.eu-central-1.amazoncognito.com/oauth2/token"
        self.access_token = None
        self.version = "v2"
        self.host = f"https://api.scoutmaster.nl/{self.version}/"
        self.output_format = "df"
    
    def _check_auth(self):
        if not self.access_token:
            raise Exception("You must authenticate first.")
        
    def _get_headers(self):
        """Helper to return headers with the access token."""
        self._check_auth()
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
    def _format_output(self, data):
        """Helper to format API response according to self.output_format."""
        if self.output_format == "json":
            return data
        elif self.output_format == "df":
            return pd.DataFrame(data)
        elif self.output_format == "gdf":
            if isinstance(data, dict) and "features" in data:
                return gpd.GeoDataFrame.from_features(data["features"])
            return gpd.GeoDataFrame.from_features(data)
        elif self.output_format == "geojson":
            # Return GeoJSON dict
            if isinstance(data, gpd.GeoDataFrame):
                return data.__geo_interface__  # Converts GeoDataFrame to GeoJSON-like dict
            elif isinstance(data, dict) and "features" in data:
                return data  # Already a GeoJSON dict
            else:
                # Wrap data into a GeoJSON FeatureCollection if possible
                return {"type": "FeatureCollection", "features": data}
        else:
            raise ValueError("output_format must be 'df', 'gdf', 'geojson', or 'json'")
    
    def _get(self, endpoint, params=None, verbose=False):
        """Internal GET request helper."""
        try:
            response = requests.get(
                f"{self.host}{endpoint}",
                headers=self._get_headers(),
                params=params  # requests will handle encoding
            )
            response.raise_for_status()
            response_json = response.json()
            data = response_json.get("data", response_json)
            if verbose:
                count = response_json.get("count", len(data))
                display(HTML(f'Response count: <span style="color:#28a745">{count}</span>'))
            return data
        except requests.exceptions.RequestException as e:
            raise Exception(f"GET request failed: {e}")
        
    def authenticate(self, client_id, client_secret):
        data = {
            'grant_type': 'client_credentials',
        }
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(client_id, client_secret)
        response = self.session.post(self.token_url, data=data, headers={'Accept': 'application/json'})
        if response.status_code == 200:
            self.access_token = response.json().get('access_token')
            if not self.access_token:
                raise Exception("Authentication succeeded but no access_token was returned.")
            print("✅ Successfully authenticated ScoutMaster API")
        else:
            raise Exception(f"Authentication failed: {response.status_code} {response.text}")
        
    def crops(self, sort_by=None, order=None, limit=None, page=None, verbose=False):
        """Retrieve the list of crops from the API with optional sorting and pagination."""
        endpoint = "crops"
        params = {}

        # Add optional parameters if provided
        if sort_by:
            params["sort_by"] = sort_by
        if order:
            params["order"] = order
        if limit:
            params["limit"] = limit
        if page:
            params["page"] = page

        data = self._get(endpoint, params=params, verbose=verbose)
        return self._format_output(data)

    def crop_varieties(self, crop_code):
        self._check_auth()
        data = self._get(f"crops/{crop_code}/varieties")
        return self._format_output(data)

    def fields(self, project_id):
        endpoint = f"fields?project_id={project_id}"
        if self.output_format in ["geojson", "gdf"]:
            endpoint += "&output=geojson"
        data = self._get(endpoint)
        return self._format_output(data)
    
    def fields_create(self, project_collection_id, fields_data):
        """
        Create new fields in the specified project collection.

        Args:
            project_collection_id (str): The ID of the project collection.
            fields_data (list): List of field dicts to create.

        Returns:
            pd.DataFrame or dict: Created fields as DataFrame or JSON.
        """
        self._check_auth()
        endpoint = f"{self.host}fields?project_collection_id={project_collection_id}"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        try:
            response = requests.post(endpoint, json=fields_data, headers=headers)
            response_json = response.json()
            if response.status_code == 200 or response.status_code == 201:
                # data = response_json.get("data", response_json)
                return pd.DataFrame(response_json) if self.output_format == "df" else response_json
            else:
                raise Exception(f"Failed to create fields: {response.status_code} {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")
        
    def fields_update(self, field_id, name, properties, geometry):
        """
        Update an existing field's name, properties, and geometry.

        Args:
            field_id (str or int): The ID of the field to update.
            name (str): The new name for the field.
            properties (dict): Properties to update.
            geometry (dict): GeoJSON geometry (Polygon).

        Returns:
            pd.DataFrame or dict: Updated field as DataFrame or JSON.
        """
        self._check_auth()
        endpoint = f"{self.host}fields"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        body = {
            "id": field_id,
            "name": name,
            "properties": properties,
            "geometry": geometry,
        }
        try:
            response = requests.put(endpoint, json=body, headers=headers)
          
            response_json = response.json()
            if response.status_code in [200, 201]:
                return pd.DataFrame(response_json) if self.output_format == "df" else response_json
            else:
                raise Exception(f"Failed to update field: {response.status_code} {response.text}")
        except requests.exceptions.RequestException as e:
                raise Exception(f"PUT request failed: {e}")
            
    def fields_delete(self, field_id):
        """
        Delete a field by ID (sending ID in request body).

        Args:
            field_id (str or int): The ID of the field to delete.

        Returns:
            dict or pd.DataFrame: API response confirming deletion.
        """
        self._check_auth()
        endpoint = f"{self.host}fields"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        body = {"id": field_id}

        try:
            response = requests.delete(endpoint, json=body, headers=headers)
            response_json = response.json() if response.text else {}

            if response.status_code in [200, 204]:
                if self.output_format == "df":
                    return pd.DataFrame([response_json]) if response_json else pd.DataFrame()
                return response_json or {"status": "success", "message": f"Field {field_id} deleted successfully"}
            else:
                raise Exception(f"Failed to delete field: {response.status_code} {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"DELETE request failed: {e}")

        
    def layers_sources(self):
        """
        Retrieves available layer sources.
        Returns:
            pd.DataFrame or list: Layer sources as DataFrame or JSON list.
        """
        self._check_auth()
        endpoint = "layers/sensors"
        data = self._get(endpoint)
        return pd.DataFrame(data) if self.output_format == "df" else data
    
    def layers_types(self, layer_source_id=None):
        """
        Retrieves available layer types, optionally filtered by layer source.
        Args:
            layer_source_id (str, optional): Filter by layer source ID.
        Returns:
            pd.DataFrame or list: Layer types as DataFrame or JSON list.
        """
        self._check_auth()
        endpoint = "layers/types"
        if layer_source_id is not None:
            endpoint += f"?layerSourceId={layer_source_id}"
        data = self._get(endpoint)
        return pd.DataFrame(data) if self.output_format == "df" else data
    
    def layers(self, field_id, layer_type_id=None, start_date=None, end_date=None):
        self._check_auth()
        endpoint = f"layers/{field_id}/"
        params = []
        if layer_type_id is not None:
            params.append(f"layer_type_id={layer_type_id}")
        if start_date is not None:
            params.append(f"start_date={start_date}")
        if end_date is not None:
            params.append(f"end_date={end_date}")
        if params:
            endpoint += "?" + "&".join(params)
        data = self._get(endpoint)
        return pd.DataFrame(data) if self.output_format == "df" else data
    
    def layers_stacks(self, field_id, layer_sensor_id=None, start_date=None, end_date=None):
        self._check_auth()
        endpoint = f"layers/{field_id}/stacks"
        params = []
        if layer_sensor_id is not None:
            params.append(f"layer_sensor_id={layer_sensor_id}")
        if start_date is not None:
            params.append(f"start_date={start_date}")
        if end_date is not None:
            params.append(f"end_date={end_date}")
        if params:
            endpoint += "?" + "&".join(params)
        data = self._get(endpoint)
        return pd.DataFrame(data) if self.output_format == "df" else data
    
    def layers_stats(self, layer_id):
        self._check_auth()
        endpoint = f"layers/{layer_id}/statistics"
        data = self._post(endpoint)
        return pd.DataFrame(data) if self.output_format == "df" else data
    
    def benchmark(self, peergroup_ids, ref_field_id=None):
        self._check_auth()
        endpoint = "benchmark"
        payload = {
            "peergroup_ids": peergroup_ids
        }
        if ref_field_id is not None:
            payload["reference_field_id"] = ref_field_id
        data = self._post(endpoint, payload=payload)
        return pd.DataFrame(data["benchmark_data"]) if self.output_format == "df" else data
    
    def get_cultivation_calendar(self, field_id):
        """
        Retrieves the cultivation calendar for a given field.
        Args:
            field_id (str or int): The ID of the field.
        Returns:
            dict or pd.DataFrame: Cultivation calendar data as JSON or DataFrame.
        """
        self._check_auth()
        endpoint = f"calendar/{field_id}"
        data = self._get(endpoint)
        return pd.DataFrame(data) if self.output_format == "df" else data

    def post_cultivation_calendar(self, field_id, crop_code, crop_variety_code, plant_date, harvest_date):
        """
        Posts a cultivation calendar entry for a given field.

        Args:
            field_id (str or int): The ID of the field.
            crop_code (int): The crop code.
            crop_variety_code (int): The crop variety code.
            plant_date (str): Planting date in 'YYYY-MM-DD' format.
            harvest_date (str): Harvest date in 'YYYY-MM-DD' format.

        Returns:
            dict or pd.DataFrame: API response as JSON or DataFrame.
        """
        self._check_auth()
        endpoint = f"calendar/{field_id}"
        payload = {
            "crop_code": crop_code,
            "crop_variety_code": crop_variety_code,
            "plant_date": plant_date,
            "harvest_date": harvest_date
        }

        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(f"{self.host}{endpoint}", headers=headers, json=payload)
            response_json = response.json()
            if response.status_code in [200, 201]:
                return response_json
            else:
                raise Exception(f"Failed to post cultivation calendar: {response.status_code} {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"POST request failed: {e}")

    def get_subscriptions(self, field_id):
        """
        Retrieves the cultivation calendar for a given field.
        Args:
            field_id (str or int): The ID of the field.
        Returns:
            dict or pd.DataFrame: Cultivation calendar data as JSON or DataFrame.
        """
        self._check_auth()
        endpoint = f"subscription/{field_id}"
        data = self._get(endpoint)
        return pd.DataFrame(data) if self.output_format == "df" else data
    
    
    def post_subscription(self, field_id, user_id, subscription_type=None):
        """
        Creates a subscription for a given field and user.
        Args:
            field_id (str or int): The ID of the field.
            user_id (str or int): The ID of the user to subscribe.
            subscription_type (str, optional): The type of subscription.
        Returns:
            dict or pd.DataFrame: API response as JSON or DataFrame.
        """
        self._check_auth()
        endpoint = f"subscription/{field_id}/"
        params = {
            "user_id": user_id
        }
        if subscription_type:
            params["subscription_type"] = subscription_type
        url = f"{self.host}{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        try:
            response = requests.post(url, headers=headers, params=params)
            response_json = response.json()
            if response.status_code in [200, 201]:
                return pd.DataFrame(response_json) if self.output_format == "df" else response_json
            else:
                raise Exception(f"Failed to post subscription: {response.status_code} {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"POST request failed: {e}")



        
    def _post(self, endpoint, payload=None):
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        try:
            response = requests.post(f"{self.host}{endpoint}", headers=headers, json=payload or {})
            response_json = response.json()
            if response.status_code == 201:
                data = response_json.get("data", [])
                count = response_json.get("count", len(data))
                return data
            elif response.status_code == 404:
                message = response_json.get("message", "No data found")
                return []
            else:
                raise Exception(f"Failed to POST to {endpoint}: {response.status_code} {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"POST request failed: {e}")

        





