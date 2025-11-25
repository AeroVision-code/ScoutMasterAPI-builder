from IPython.display import display, HTML
import pandas as pd
import geopandas as gpd
from requests.auth import HTTPBasicAuth
import requests
import json

class BaseAPI:
    """Core HTTP requests and output formatting"""
    def __init__(self, dev=False, output_format="df"):
        self.token_url = "https://eu-central-1fq4qt7w6q.auth.eu-central-1.amazoncognito.com/oauth2/token"
        self.access_token = None
        self.version = "v2"
        self.host = f"https://dev-api.scoutmaster.nl/{self.version}/" if dev else f"https://api.scoutmaster.nl/{self.version}/"
        self.output_format = output_format
        self.lang = "en"

    def authenticate(self, client_id, client_secret):
        data = {'grant_type': 'client_credentials'}
        session = requests.Session()
        session.auth = HTTPBasicAuth(client_id, client_secret)
        response = session.post(self.token_url, data=data, headers={'Accept': 'application/json'})
        response.raise_for_status()
        if response.status_code == 200:
            self.access_token = response.json().get('access_token')
            if not self.access_token:
                raise Exception("Authentication succeeded but no access_token was returned.")
            print("✅ Successfully authenticated ScoutMaster API")
            print("HOST:", self.host)
        else:
            raise Exception(f"Authentication failed: {response.status_code} {response.text}")

    def _check_auth(self):
        if not self.access_token:
            raise Exception("Call authenticate() first")

    def _get_headers(self):
        self._check_auth()
        return {'Authorization': f'Bearer {self.access_token}', 'Content-Type': 'application/json'}

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

    def _format_output(self, data):
        """Helper to format API response according to self.output_format."""
        if self.output_format == "json":
            return data
        elif self.output_format == "df":
            return pd.DataFrame(data)
        elif self.output_format == "gdf":
            if isinstance(data, dict) and "features" in data:
                gdf = gpd.GeoDataFrame.from_features(data["features"])
            else:
                gdf = gpd.GeoDataFrame.from_features(data)

            # Set CRS only if not already defined
            if gdf.crs is None:
                gdf.set_crs(epsg=4326, inplace=True)

            return gdf
        elif self.output_format == "geojson":
            if isinstance(data, gpd.GeoDataFrame):
                geojson_dict = data.__geo_interface__
            elif isinstance(data, dict) and "features" in data:
                geojson_dict = data
            else:
                geojson_dict = {"type": "FeatureCollection", "features": data}

            # Serialize to valid JSON string if needed
            return json.dumps(geojson_dict)  # <-- Ensures proper double quotes
        else:
            raise ValueError("output_format must be 'df', 'gdf', 'geojson', or 'json'")
