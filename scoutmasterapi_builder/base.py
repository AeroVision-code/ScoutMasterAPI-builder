import time
import functools
import pandas as pd
import geopandas as gpd
from requests.auth import HTTPBasicAuth
import requests
import json
from warnings import warn


def conceptual(func):
    """Mark a client method as targeting a ⚠️ Conceptual endpoint.

    Conceptual endpoints are documented in the OpenAPI spec but not yet
    implemented server-side and may change significantly. Calling a decorated
    method emits a warning so users know the result is not stable.
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        warn(
            f"'{func.__name__}' calls a ⚠️ Conceptual ScoutMaster endpoint that is "
            f"not yet implemented server-side and may change significantly.",
            stacklevel=2,
        )
        return func(self, *args, **kwargs)
    return wrapper


def conceptual_class(cls):
    """Apply @conceptual to every public method of a class.

    Use for mixins whose endpoints are all Conceptual.
    """
    for name, attr in list(vars(cls).items()):
        if callable(attr) and not name.startswith("_"):
            setattr(cls, name, conceptual(attr))
    return cls
from shapely.wkt import loads as wkt_loads
from shapely.wkb import loads as wkb_loads
from shapely.geometry import mapping, shape
import binascii
from shapely.wkt import loads as wkt_loads
from shapely.wkb import loads as wkb_loads
from shapely.geometry import mapping, shape
import binascii

class BaseAPI:
    """Core HTTP requests and output formatting"""
    def __init__(self, dev=False, output_format="df", version="v3", verbose=True,
                 spatial=False):
        self.verbose = verbose  # toggle helper/status prints on or off
        self.token_url = "https://eu-central-1fq4qt7w6q.auth.eu-central-1.amazoncognito.com/oauth2/token"
        self.access_token = None
        # Credentials + expiry are cached so the token can be reused and
        # transparently re-fetched only when it is about to expire.
        self._client_id = None
        self._client_secret = None
        self._token_expiry = 0.0  # epoch seconds when the cached token expires
        self._expiry_skew = 60    # refresh this many seconds before actual expiry
        self.version = version
        self.api = "https://dev-api.scoutmaster.nl" if dev else "https://api.scoutmaster.nl"
        self.host = f"{self.api}/{self.version}/"
        # output_format is the container ('df' or 'json'); `spatial` controls
        # whether geometry-bearing responses are returned geometry-aware
        # (GeoDataFrame for df, GeoJSON FeatureCollection for json).
        # Legacy values 'gdf'/'geojson' map onto (container + spatial=True).
        if output_format == "gdf":
            output_format, spatial = "df", True
        elif output_format == "geojson":
            output_format, spatial = "json", True
        if output_format not in ("df", "json"):
            raise ValueError("output_format must be 'df' or 'json' (or legacy 'gdf'/'geojson')")
        self.output_format = output_format
        self.spatial = spatial
        self.lang = "en"
        self._log(f"Initialized ScoutMaster API with host: {self.host}")

    def _log(self, *args, **kwargs):
        """Print only when verbose is enabled."""
        if self.verbose:
            print(*args, **kwargs)

    def authenticate(self, client_id, client_secret):
        # Cache credentials so the token can be re-fetched automatically on expiry.
        self._client_id = client_id
        self._client_secret = client_secret
        self._fetch_token()
        self._log("✅ Successfully authenticated ScoutMaster API")
        self._log("ENVIRONMENT: ", "DEV" if self.api.endswith("dev-api.scoutmaster.nl") else "PROD")
        self._log("HOST:", self.host)

    def _fetch_token(self):
        """Request a fresh access token via the client_credentials grant.

        The client_credentials flow does not issue refresh tokens, so the
        correct pattern is to cache the access token and re-request it only
        when it is close to expiring (tracked via `expires_in`).
        """
        data = {'grant_type': 'client_credentials'}
        session = requests.Session()
        session.auth = HTTPBasicAuth(self._client_id, self._client_secret)
        response = session.post(self.token_url, data=data, headers={'Accept': 'application/json'})
        response.raise_for_status()
        if response.status_code != 200:
            raise Exception(f"Authentication failed: {response.status_code} {response.text}")

        payload = response.json()
        self.access_token = payload.get('access_token')
        if not self.access_token:
            raise Exception("Authentication succeeded but no access_token was returned.")

        # Cognito returns the token lifetime in seconds (default 3600).
        expires_in = payload.get('expires_in', 3600)
        self._token_expiry = time.time() + expires_in

    def _token_valid(self):
        return bool(self.access_token) and time.time() < (self._token_expiry - self._expiry_skew)

    def _ensure_token(self):
        """Reuse the cached token; transparently re-fetch it when near expiry."""
        if self._token_valid():
            return
        if not self._client_id or not self._client_secret:
            raise Exception("Call authenticate() first")
        self._fetch_token()

    def _check_auth(self):
        self._ensure_token()

    def _get_headers(self):
        self._check_auth()
        return {'Authorization': f'Bearer {self.access_token}', 'Content-Type': 'application/json'}

    def _get(self, endpoint, params=None, verbose=False):
        """Internal GET request helper."""
        try:
            self._check_auth()
        
            response = requests.get(
                f"{self.host}{endpoint}",
                headers=self._get_headers(),
                params=params  # requests will handle encoding
            )
            response.raise_for_status()
            response_json = response.json()
            data = response_json.get("data", response_json)
            if verbose:
                count = response_json.get("count", len(data) if hasattr(data, "__len__") else 1)
                self._log(f"GET {endpoint} → {count} record(s)")
            return data
        except requests.exceptions.RequestException as e:
            rtn_text = response.text.lower()
            code = response.status_code
            if (code // 100 == 4) and ("not found" in rtn_text) or ("validation failed" in rtn_text):
                warn(response.text)
                return []
            else:
                raise Exception(f"GET request failed: {e}")

    def _post(self, endpoint, payload=None, files=None):
        """
        Internal helper to send a POST request to the API.
        
        Supports JSON payloads (default) or multipart/form-data if files are provided.
        """
        self._check_auth()

        # Default headers for JSON
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }

        # If sending JSON (no files)
        if files is None:
            headers['Content-Type'] = 'application/json'
            request_args = {"json": payload or {}}
        else:
            # multipart/form-data automatically set by requests if files are provided
            request_args = {"data": payload or {}, "files": files}

        try:
            response = requests.post(f"{self.host}{endpoint}", headers=headers, **request_args)

            # First, check if the response has content
            if response.content:
                try:
                    response_json = response.json()
                except ValueError:
                    # Non-JSON response
                    raise Exception(
                        f"POST request to {endpoint} did not return valid JSON. "
                        f"Response content: {response.text}"
                    )
            else:
                response_json = {}

            # Handle response based on status code
            if response.status_code in [200, 201]:
                return response_json.get("data", response_json)
            elif response.status_code == 404:
                return []
            else:
                raise Exception(
                    f"Failed POST request to {endpoint}: {response.status_code} {response.text}"
                )

        except requests.exceptions.RequestException as e:
            raise Exception(f"POST request failed: {e}")
        

    def _patch(self, endpoint, payload=None):
        """Internal helper to send a PATCH request to the API."""
        self._check_auth()
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
        }
        try:
            response = requests.patch(
                f"{self.host}{endpoint}",
                headers=headers,
                json=payload or {},
            )
            if response.content:
                try:
                    response_json = response.json()
                except ValueError:
                    raise Exception(
                        f"PATCH request to {endpoint} did not return valid JSON. "
                        f"Response content: {response.text}"
                    )
            else:
                response_json = {}
            if response.status_code in (200, 201):
                return response_json.get("data", response_json)
            else:
                raise Exception(
                    f"Failed PATCH request to {endpoint}: {response.status_code} {response.text}"
                )
        except requests.exceptions.RequestException as e:
            raise Exception(f"PATCH request failed: {e}")

    def _delete(self, endpoint):
        """Internal helper to send a DELETE request to the API."""
        self._check_auth()
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
        }
        try:
            response = requests.delete(f"{self.host}{endpoint}", headers=headers)
            if response.status_code == 204:
                return True
            if response.content:
                try:
                    response_json = response.json()
                except ValueError:
                    raise Exception(
                        f"DELETE request to {endpoint} did not return valid JSON. "
                        f"Response content: {response.text}"
                    )
            else:
                response_json = {}
            if response.status_code == 200:
                return response_json.get("data", response_json)
            else:
                raise Exception(
                    f"Failed DELETE request to {endpoint}: {response.status_code} {response.text}"
                )
        except requests.exceptions.RequestException as e:
            raise Exception(f"DELETE request failed: {e}")
    def _parse_geometry(self, geom):
        """Parse geometry from string (WKT/WKB) or dict (GeoJSON) to shapely geometry."""
        if geom is None:
            return None
        if isinstance(geom, dict):
            return shape(geom)  # already GeoJSON
        if isinstance(geom, str):
            try:
                # Try WKT first (e.g. "POLYGON ((...))")
                return wkt_loads(geom)
            except Exception:
                try:
                    # Try hex-encoded WKB
                    return wkb_loads(binascii.unhexlify(geom))
                except Exception:
                    raise ValueError(f"Cannot parse geometry string: {geom[:100]}")
        raise ValueError(f"Unexpected geometry type: {type(geom)}")

    def _has_geometry(self, data):
        """True if the response carries geometry (a GeoJSON FeatureCollection,
        a single feature/record with a 'geometry' key, or a list of such records).
        """
        if isinstance(data, dict):
            return "features" in data or "geometry" in data
        if isinstance(data, list) and data:
            return isinstance(data[0], dict) and "geometry" in data[0]
        return False

    def _to_geodataframe(self, data):
        """Build a GeoDataFrame from a FeatureCollection or list/dict of records
        whose 'geometry' may be GeoJSON, WKT, or hex-WKB."""
        if isinstance(data, dict) and "features" in data:
            gdf = gpd.GeoDataFrame.from_features(data["features"])
        else:
            items = data if isinstance(data, list) else [data]
            rows = []
            for item in items:
                item = dict(item)
                item["geometry"] = self._parse_geometry(item.get("geometry"))
                rows.append(item)
            gdf = gpd.GeoDataFrame(rows, geometry="geometry")
        if "geometry" in gdf.columns and gdf.crs is None:
            gdf.set_crs(epsg=4326, inplace=True)
        return gdf

    def _format_output(self, data):
        """Format an API response according to self.output_format + self.spatial.

        output_format selects the container ('df' or 'json'); spatial selects
        whether geometry-bearing responses are returned geometry-aware. When
        spatial is requested but the endpoint returns no geometry, formatting
        falls back to the plain container so non-spatial endpoints keep working.
        """
        spatial = bool(getattr(self, "spatial", False)) and self._has_geometry(data)

        if self.output_format == "json":
            if spatial:
                if isinstance(data, dict) and "features" in data:
                    return data  # already a FeatureCollection
                return self._to_geodataframe(data).__geo_interface__
            return data

        if self.output_format == "df":
            if spatial:
                return self._to_geodataframe(data)
            # plain DataFrame
            if isinstance(data, dict) and "features" in data:
                # FeatureCollection but non-spatial: flatten properties + geometry
                rows = [{**f.get("properties", {}), "geometry": f.get("geometry")}
                        for f in data["features"]]
                return pd.DataFrame(rows)
            if isinstance(data, dict):
                data = [data]  # normalize single object to list
            return pd.DataFrame(data)

        raise ValueError("output_format must be 'df' or 'json'")
        
    def _validate_numeric_fields(self, data: dict, fields: list[str]):
        for field in fields:
            if field in data and data[field] is not None:
                try:
                    data[field] = float(data[field])
                except (ValueError, TypeError):
                    raise ValueError(f"'{field}' must be a number if provided.")
