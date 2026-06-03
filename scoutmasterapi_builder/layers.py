import mimetypes
import os

class Layers:
    def layers(self, field_id, layer_type_id=None, start_date=None, end_date=None):
        """
        Get all layers for the given field possibly filtered by the given layer
            type, start date and end date
        Args:
            field_id (str): The ID of the field
            layer_type_id (str): The ID of the layer type of interest - if any
            start_date (str): the relevant start date - if any
            end_date (str): the relevant end date - if any
        Returns:
            pd.DataFrame or list: a DataFrame or JSON list with data on the relevant layers
        """
        endpoint = f"fields/{field_id}/layers"
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
        Trigger statistics calculation for a layer.
        Args:
            layer_id (int): Numeric layer ID.
        Returns:
            dict: Updated layer data including computed statistics.
        """
        endpoint = f"layers/{layer_id}/statistics"
        data = self._post(endpoint)
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

