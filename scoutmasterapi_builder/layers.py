import mimetypes
import os

from .base import conceptual


class Layers:
    def layers(self, field_id, layer_type_id=None, start_date=None, end_date=None,
               page=None, limit=None, order=None, sort_by=None):
        """
        Get all layers for the given field, optionally filtered by layer type and
        acquisition date range, with sorting and pagination.
        Args:
            field_id (str): The ID of the field
            layer_type_id (str, optional): Filter to a single layer type.
            start_date (str, optional): Acquisition timestamp lower bound.
            end_date (str, optional): Acquisition timestamp upper bound.
            page (int, optional): Page number (default 1).
            limit (int, optional): Results per page. Omit to return all.
            order (str, optional): 'asc' or 'desc'.
            sort_by (str, optional): 'acquired_at', 'created_at' or 'updated_at'.
        Returns:
            pd.DataFrame or list: a DataFrame or JSON list with data on the relevant layers
        """
        endpoint = f"fields/{field_id}/layers"
        params = {}
        if layer_type_id is not None: params["layer_type_id"] = layer_type_id
        if start_date is not None: params["start_date"] = start_date
        if end_date is not None: params["end_date"] = end_date
        if page: params["page"] = page
        if limit: params["limit"] = limit
        if order: params["order"] = order
        if sort_by: params["sort_by"] = sort_by
        data = self._get(endpoint, params=params)
        return self._format_output(data)

    def project_layers(self, project_id, layer_type_id=None, start_date=None,
                       end_date=None, page=None, limit=None, order=None, sort_by=None):
        """
        Get all layers in a project (across its fields), with the same filters as
        the field-layers endpoint plus sorting and pagination.
        Args:
            project_id (str): UUID of the project.
            layer_type_id (str, optional): Filter to a single layer type.
            start_date (str, optional): Acquisition timestamp lower bound.
            end_date (str, optional): Acquisition timestamp upper bound.
            page (int, optional): Page number (default 1).
            limit (int, optional): Results per page. Omit to return all.
            order (str, optional): 'asc' or 'desc'.
            sort_by (str, optional): 'acquired_at', 'created_at' or 'updated_at'.
        Returns:
            pd.DataFrame or list: Layers as DataFrame or JSON list.
        """
        endpoint = f"projects/{project_id}/layers"
        params = {}
        if layer_type_id is not None: params["layer_type_id"] = layer_type_id
        if start_date is not None: params["start_date"] = start_date
        if end_date is not None: params["end_date"] = end_date
        if page: params["page"] = page
        if limit: params["limit"] = limit
        if order: params["order"] = order
        if sort_by: params["sort_by"] = sort_by
        data = self._get(endpoint, params=params)
        return self._format_output(data)

    def layer_by_id(self, layer_id):
        """
        Get layer by id
        Args:
            layer_id (str): The ID of the layer of interest
        Returns:
            pd.DataFrame or list: a DataFrame or JSON list with data on the indicated layer.
        """
        endpoint = f"layers/{layer_id}"
        data = self._get(endpoint)
        return self._format_output(data)

    def layer_export(self, layer_id, format="png"):
        """
        Get a URL of the image to download - in the specified format
        Args:
            layer_id (str):  The ID of the layer of interest
            format (str): the wanted format
        Returns:
            pd.DataFrame or list: a DataFrame or JSON list with data - incl. the URL of the image.
        """
        endpoint = f"layers/{layer_id}/export"
        endpoint += f"?format={format}"
        data = self._get(endpoint)
        return data

    @conceptual
    def layer_create(self, field_id, type_id, acquired_at, file_path, acquired_at_end_date=None):
        """
        Create a layer
        Args:
            field_id (str): The ID of the field
            type_id (str): The ID of the layer type
            acquired_at (str): The date that the layer was acquired
            file_path (str): The local path to the file
        Returns:
            An http response with a status code
        """
        endpoint = f"fields/{field_id}/layers"

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # ✅ detect mimetype from file extension
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type = 'application/octet-stream'

        # ✅ explicitly set filename and content type
        files = {
            "file": (
                os.path.basename(file_path),  # filename
                open(file_path, "rb"),         # file handle
                mime_type,                     # content type
            )
        }
        data = {"acquired_at": acquired_at,  "type_id": type_id}
        if acquired_at_end_date is not None:
            data["acquired_at_end_date"] = acquired_at_end_date

        try:
            response = self._post(endpoint, payload=data, files=files)
        finally:
            files["file"][1].close()  # close the file handle (index 1 in tuple)

        return response

    def layers_upload_stats(self, layer_id, data, path, preview):
        """
        Adds layer statistics
        Args:
            layer_id (str): The ID of the field
            data (dict): metadata and statistics
            path (str): path
            preview (str): path to preview image
        Returns:
            An http response with a status code
        """
        endpoint = f"layers/{layer_id}/statistics"
        statistics = {"message": "Bla bla",
                      "data": data,
                      "path": path,
                      "preview": {
                          "path": preview["path"],
                          "format": preview["format"]
                      }
        }
        data = self._post(endpoint, statistics)
        #TODO: complete!

    def layer_delete(self, layer_id):
        """
        Delete a layer by its numeric ID.
        Args:
            layer_id (int): Numeric layer ID.
        Returns:
            dict: Contains 'message' confirming deletion.
        """
        endpoint = f"layers/{layer_id}"
        data = self._delete(endpoint)
        return data

    @conceptual
    def layer_metadata(self, layer_id):
        """
        Get metadata for a layer.
        Args:
            layer_id (int): Numeric layer ID.
        Returns:
            dict: Layer metadata.
        """
        endpoint = f"layers/{layer_id}/metadata"
        data = self._get(endpoint)
        return data

    @conceptual
    def layer_metadata_post(self, layer_id, metadata):
        """
        Post/update metadata for a layer.
        Args:
            layer_id (int): Numeric layer ID.
            metadata (dict): Arbitrary key-value metadata to store.
        Returns:
            dict: Contains 'message' and 's3_key'.
        """
        endpoint = f"layers/{layer_id}/metadata"
        data = self._post(endpoint, payload=metadata)
        return data

    def layer_statistics(self, layer_id):
        """
        (Re)compute and store summary statistics for a layer (POST).
        Args:
            layer_id (int): Numeric layer ID.
        Returns:
            dict: The computed statistics.
        """
        endpoint = f"layers/{layer_id}/statistics"
        data = self._post(endpoint)
        return data

    def layer_statistics_get(self, layer_id):
        """
        Return the stored summary statistics for a layer (GET). Use
        layer_statistics() to (re)compute them.
        Args:
            layer_id (int): Numeric layer ID.
        Returns:
            dict: The stored statistics (mean, min, max, std, etc.).
        """
        endpoint = f"layers/{layer_id}/statistics"
        data = self._get(endpoint)
        return data

    @conceptual
    def layer_timeseries(self, field_id, layer_type_id, geometry):
        """
        Return a time-ordered list of (date, mean, std, min, max) for a field,
        layer type, and area of interest.
        Args:
            field_id (str): UUID of the field.
            layer_type_id (str): UUID of the layer type.
            geometry (str): Area of interest as a WKT string.
        Returns:
            dict: TimeseriesResponse with a 'data' list.
        """
        endpoint = f"fields/{field_id}/layers/timeseries"
        payload = {"layer_type_id": layer_type_id, "geometry": geometry}
        data = self._post(endpoint, payload)
        return data

    def layer_histogram(self, layer_id, bins=50, band=1):
        """
        Get a histogram of pixel values for a layer.
        Args:
            layer_id (int): Numeric layer ID.
            bins (int, optional): Number of histogram bins (default 50).
            band (int, optional): Band index (default 1).
        Returns:
            dict: Histogram data including bins, total_pixels, valid_pixels, min_value, max_value.
        """
        endpoint = f"layers/{layer_id}/histogram"
        params = {"bins": bins, "band": band}
        data = self._get(endpoint, params=params)
        return data

