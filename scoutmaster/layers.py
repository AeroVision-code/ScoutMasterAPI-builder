import mimetypes
import os


class Layers:
    def layers(self, field_id, layer_type_id=None, start_date=None, end_date=None):
        endpoint = f"fields/{field_id}/layers"
        params = {}
        if layer_type_id is not None:
            params["layer_type_id"] = layer_type_id
        if start_date is not None:
            params["start_date"] = start_date
        if end_date is not None:
            params["end_date"] = end_date
        data = self._get(endpoint, params=params)
        return self._format_output(data)

    def layers_uploadurl(self, field_id, layer_type_id, acquired_at):
        """Request a presigned upload URL for a layer file."""
        endpoint = "layers/upload-url"
        payload = {
            "field_id": field_id,
            "layer_type_id": layer_type_id,
            "acquired_at": acquired_at,
        }
        data = self._post(endpoint, payload=payload)
        return data

    def layers_rasters(self, layer_id):
        endpoint = f"layers/{layer_id}/raster"
        data = self._get(endpoint)
        return data

    def layer_create(self, field_id, type_id, acquired_at, file_path):
        """
        Upload a new layer file for a field.

        Args:
            field_id (str): UUID of the field.
            type_id (str): UUID of the layer type.
            acquired_at (str): ISO8601 acquisition timestamp.
            file_path (str): Local path to the layer file.

        Returns:
            list or dict: Created layer data.
        """
        endpoint = f"fields/{field_id}/layers"
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type = "application/octet-stream"
        files = {
            "file": (
                os.path.basename(file_path),
                open(file_path, "rb"),
                mime_type,
            )
        }
        data = {"acquired_at": acquired_at, "type_id": type_id}
        try:
            response = self._post(endpoint, payload=data, files=files)
        finally:
            files["file"][1].close()
        return response

    def layer_by_id(self, layer_id):
        """
        Get a single layer by its numeric ID.

        Args:
            layer_id (int): Numeric layer ID.

        Returns:
            dict: Layer data.
        """
        endpoint = f"layers/{layer_id}"
        data = self._get(endpoint)
        return data

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

    def layer_export(self, layer_id, format):
        """
        Request an export download URL for a layer.

        Args:
            layer_id (int): Numeric layer ID.
            format (str): Export format — one of 'tiff', 'png', 'geojson',
                          'shapefile', 'geopackage', 'csv', 'svg'.

        Returns:
            dict: Export data including download_url, filename, format, expires_in.
        """
        allowed = {"tiff", "png", "geojson", "shapefile", "geopackage", "csv", "svg"}
        if format not in allowed:
            raise ValueError(f"format must be one of: {sorted(allowed)}")
        endpoint = f"layers/{layer_id}/export"
        data = self._get(endpoint, params={"format": format})
        return data

    def layer_statistics(self, layer_id):
        """
        Trigger statistics calculation for a layer.

        Args:
            layer_id (int): Numeric layer ID.

        Returns:
            dict: Updated layer data including computed statistics.
        """
        endpoint = f"layers/{layer_id}/statistics"
        data = self._post(endpoint)
        return data
