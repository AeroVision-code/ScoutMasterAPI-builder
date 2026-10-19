import time
import functools
import hashlib
import threading
import mimetypes
import os.path
import pandas as pd
import geopandas as gpd
from requests.auth import HTTPBasicAuth
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests
import json
from warnings import warn


class ScoutMasterAPIError(Exception):
    """A failed ScoutMaster API call. `status_code` is None for network errors."""
    def __init__(self, message, status_code=None, response_text=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


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

class BaseAPI:
    """Core HTTP requests and output formatting"""
    # Process-wide token cache: (token_url, client_id, secret hash) -> (token, expiry).
    # In memory only; nothing is written to disk.
    _shared_tokens = {}
    _token_lock = threading.Lock()
    # Items per request when fetching all pages of a list (the API's maximum limit).
    PAGE_SIZE = 100

    def __init__(self, dev=False, output_format="df", version="v3", verbose=True,
                 spatial=False, timeout=60, retries=3):
        self.verbose = verbose  # toggle helper/status prints on or off
        # Seconds to wait for the server to connect/respond, per request.
        self.timeout = timeout
        # One session per client keeps connections open between calls. The
        # adapter retries connection errors, and 429/5xx responses on
        # idempotent methods (GET/PUT/DELETE) only, so a POST that may have
        # reached the server is never sent twice. Retry-After is respected.
        # A read timeout is retried once at most, so a hanging endpoint costs
        # about 2x timeout rather than (retries + 1)x.
        retry = Retry(
            total=retries, read=min(retries, 1), backoff_factor=1,
            status_forcelist=(429, 500, 502, 503, 504),
            raise_on_status=False,
        )
        self._session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry)
        self._session.mount("https://", adapter)
        self._session.mount("http://", adapter)
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

    def authenticate(self, client_id=None, client_secret=None):
        """Authenticate with client credentials.

        Without arguments, the SM_CLIENT_ID and SM_CLIENT_SECRET environment
        variables are used (load a .env file first, e.g. with python-dotenv).
        """
        client_id = client_id or os.getenv("SM_CLIENT_ID")
        client_secret = client_secret or os.getenv("SM_CLIENT_SECRET")
        if not client_id or not client_secret:
            raise ValueError(
                "No credentials: pass client_id and client_secret, or set the "
                "SM_CLIENT_ID and SM_CLIENT_SECRET environment variables."
            )
        # Cache credentials so the token can be re-fetched automatically on expiry.
        self._client_id = client_id
        self._client_secret = client_secret
        # Drop any token from earlier credentials; _ensure_token() then reuses a
        # still-valid shared token for these credentials or fetches a new one.
        self.access_token = None
        self._token_expiry = 0.0
        self._ensure_token()
        self._log("✅ Successfully authenticated ScoutMaster API")
        self._log("ENVIRONMENT: ", "DEV" if self.api.endswith("dev-api.scoutmaster.nl") else "PROD")
        self._log("HOST:", self.host)

    def set_access_token(self, access_token, expires_at=None):
        """Use an access token obtained elsewhere (e.g. a shared SSM cache).

        Args:
            access_token (str): Cognito access token.
            expires_at (float, optional): Expiry as epoch seconds. Without it
                the token is used until the API rejects it. If authenticate()
                was called before, a new token is fetched with those
                credentials once this one is about to expire.
        """
        self.access_token = access_token
        self._token_expiry = float("inf") if expires_at is None else float(expires_at)

    def _fetch_token(self):
        """Request a fresh access token via the client_credentials grant.

        The client_credentials flow does not issue refresh tokens, so the
        correct pattern is to cache the access token and re-request it only
        when it is close to expiring (tracked via `expires_in`).
        """
        data = {'grant_type': 'client_credentials'}
        try:
            response = self._session.post(
                self.token_url, data=data, headers={'Accept': 'application/json'},
                auth=HTTPBasicAuth(self._client_id, self._client_secret), timeout=self.timeout,
            )
        except requests.exceptions.RequestException as e:
            raise ScoutMasterAPIError(f"Authentication request failed: {e}") from e
        if response.status_code != 200:
            raise ScoutMasterAPIError(
                f"Authentication failed: {response.status_code} {response.text}",
                status_code=response.status_code, response_text=response.text,
            )

        payload = response.json()
        self.access_token = payload.get('access_token')
        if not self.access_token:
            raise Exception("Authentication succeeded but no access_token was returned.")

        # Cognito returns the token lifetime in seconds (default 3600).
        expires_in = payload.get('expires_in', 3600)
        self._token_expiry = time.time() + expires_in
        BaseAPI._shared_tokens[self._token_cache_key()] = (self.access_token, self._token_expiry)

    def _token_cache_key(self):
        # The secret is part of the key (hashed, so it isn't kept in another
        # place in clear text): authenticating with a wrong secret must not
        # pick up a token issued for the right one.
        secret_hash = hashlib.sha256(self._client_secret.encode()).hexdigest()
        return (self.token_url, self._client_id, secret_hash)

    def _token_valid(self):
        return bool(self.access_token) and time.time() < (self._token_expiry - self._expiry_skew)

    def _ensure_token(self):
        """Reuse the cached token; transparently re-fetch it when near expiry.

        Tokens are shared by all client objects in this process that use the
        same credentials, so new instances and repeated authenticate() calls
        don't each request a token of their own.
        """
        if self._token_valid():
            return
        if not self._client_id or not self._client_secret:
            # A token assigned directly to `access_token` (how older callers
            # seed one from a shared cache) has no known expiry and can't be
            # refreshed here, so use it as-is.
            if self.access_token:
                return
            raise Exception("Call authenticate() first")
        with BaseAPI._token_lock:
            shared = BaseAPI._shared_tokens.get(self._token_cache_key())
            if shared:
                self.access_token, self._token_expiry = shared
                if self._token_valid():
                    return
            self._fetch_token()

    def _check_auth(self):
        self._ensure_token()

    def _get_headers(self):
        self._check_auth()
        return {'Authorization': f'Bearer {self.access_token}', 'Content-Type': 'application/json'}

    def _request(self, method, endpoint, **kwargs):
        """Send an authenticated request on the shared session.

        Retries (connection errors; 429/5xx on idempotent methods) are handled
        by the session's adapter. Network failures and timeouts are raised as
        ScoutMasterAPIError; HTTP error statuses are left to the caller.
        """
        self._check_auth()
        headers = {'Authorization': f'Bearer {self.access_token}'}
        if "json" in kwargs:
            headers['Content-Type'] = 'application/json'
        try:
            return self._session.request(
                method, f"{self.host}{endpoint}",
                headers=headers, timeout=self.timeout, **kwargs,
            )
        except requests.exceptions.RequestException as e:
            raise ScoutMasterAPIError(f"{method} {endpoint} failed: {e}") from e

    def _raise_for_status(self, method, endpoint, response):
        if not response.ok:
            raise ScoutMasterAPIError(
                f"{method} {endpoint} failed: {response.status_code} {response.text}",
                status_code=response.status_code, response_text=response.text,
            )

    def _response_body(self, method, endpoint, response):
        """Raise on an error status, otherwise return the parsed JSON body ({} if empty)."""
        self._raise_for_status(method, endpoint, response)
        if not response.content:
            return {}
        try:
            return response.json()
        except ValueError:
            raise ScoutMasterAPIError(
                f"{method} {endpoint} did not return valid JSON. "
                f"Response content: {response.text}",
                status_code=response.status_code, response_text=response.text,
            )

    @staticmethod
    def _unwrap_data(body):
        return body.get("data", body) if isinstance(body, dict) else body

    def _response_data(self, method, endpoint, response):
        """Raise on an error status, otherwise return the body's `data` (or the body)."""
        return self._unwrap_data(self._response_body(method, endpoint, response))

    def _get_body(self, endpoint, params=None):
        """GET and return the full JSON body, or None for a 404 'not found' (with a warning)."""
        response = self._request("GET", endpoint, params=params)
        if response.status_code == 404 and "not found" in response.text.lower():
            warn(response.text)
            return None
        return self._response_body("GET", endpoint, response)

    def _get(self, endpoint, params=None, verbose=False):
        """Internal GET request helper.

        A 404 for a resource that doesn't exist returns [] with a warning;
        any other error status raises ScoutMasterAPIError.
        """
        body = self._get_body(endpoint, params)
        data = [] if body is None else self._unwrap_data(body)
        if verbose:
            count = len(data) if hasattr(data, "__len__") else 1
            self._log(f"GET {endpoint} → {count} record(s)")
        return data

    def _get_paged(self, endpoint, params=None, verbose=False):
        """GET a paginated list endpoint.

        If the caller set `limit` or `page`, this is a single request, as with
        _get(). Otherwise every page is requested (PAGE_SIZE items each, the
        API's maximum) and the items of all pages are returned as one list.
        """
        params = dict(params or {})
        if "limit" in params or "page" in params:
            return self._get(endpoint, params=params, verbose=verbose)

        items, page = [], 1
        while True:
            body = self._get_body(endpoint, {**params, "limit": self.PAGE_SIZE, "page": page})
            if body is None:
                break
            data = self._unwrap_data(body)
            if not isinstance(data, list):
                return data  # not a list after all; nothing to combine
            items.extend(data)
            pagination = body.get("pagination") if isinstance(body, dict) else None
            if pagination and pagination.get("total_pages") is not None:
                last = page >= pagination["total_pages"]
            else:
                # No pagination info: a short page is the last one, and more
                # than PAGE_SIZE items means the server ignored the limit and
                # already returned everything.
                last = len(data) != self.PAGE_SIZE
            if last or not data:
                break
            page += 1
        if verbose:
            self._log(f"GET {endpoint} → {len(items)} record(s) in {page} page(s)")
        return items

    def _post(self, endpoint, payload=None, files=None):
        """
        Internal helper to send a POST request to the API.

        Supports JSON payloads (default) or multipart/form-data if files are provided.
        """
        if files is None:
            response = self._request("POST", endpoint, json=payload or {})
        else:
            # multipart/form-data is set by requests when files are provided
            response = self._request("POST", endpoint, data=payload or {}, files=files)
        return self._response_data("POST", endpoint, response)

    def _post_file(self, endpoint, file_path, payload=None):
        """POST a local file as multipart/form-data (form field `file`)."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type = 'application/octet-stream'
        with open(file_path, "rb") as fh:
            files = {"file": (os.path.basename(file_path), fh, mime_type)}
            return self._post(endpoint, payload=payload, files=files)

    def _patch(self, endpoint, payload=None, params=None):
        """Internal helper to send a PATCH request to the API."""
        response = self._request("PATCH", endpoint, json=payload or {}, params=params)
        return self._response_data("PATCH", endpoint, response)

    def _put(self, endpoint, payload=None):
        """Internal helper to send a PUT request to the API."""
        response = self._request("PUT", endpoint, json=payload or {})
        return self._response_data("PUT", endpoint, response)

    def _delete(self, endpoint):
        """Internal helper to send a DELETE request to the API.

        Returns True on 204 No Content, otherwise the response data.
        """
        response = self._request("DELETE", endpoint)
        if response.status_code == 204:
            return True
        return self._response_data("DELETE", endpoint, response)

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
        if self.output_format not in ("json", "df"):
            raise ValueError("output_format must be 'df' or 'json'")
        
        spatial = bool(getattr(self, "spatial", False)) and self._has_geometry(data)
        is_feature_collection = isinstance(data, dict) and "features" in data

        if spatial and self.output_format == "json" and is_feature_collection:
            return data  # already a FeatureCollection

        elif spatial and self.output_format == "json":
            return self._to_geodataframe(data).__geo_interface__

        elif spatial and self.output_format == "df":
            flattened = [self._unwrap_dicts(item) for item in data]
            return self._to_geodataframe(flattened)
        
        elif self.output_format == "json":
            return data

        elif is_feature_collection:
            # FeatureCollection but non-spatial: flatten properties + geometry
            rows = [{**f.get("properties", {}), "geometry": f.get("geometry")}
                    for f in data["features"]]
            return pd.json_normalize(rows)
        
        else:
            return pd.json_normalize(data)

    def _unwrap_dicts(self, data):
        for key in ["field", "crop", "address", "layer_type", "statistics", "preview"]:
            if (key in data) and isinstance(data[key], dict):
                for subkey in list(data[key].keys()):
                    data[key + "." + subkey] = data[key][subkey]
                data.pop(key, None)
        return data

    def _validate_numeric_fields(self, data: dict, fields: list[str]):
        for field in fields:
            if field in data and data[field] is not None:
                try:
                    data[field] = float(data[field])
                except (ValueError, TypeError):
                    raise ValueError(f"'{field}' must be a number if provided.")
