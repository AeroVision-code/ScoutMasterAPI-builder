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
    
    def layers_uploadurl(self, field_id, layer_type_id, acquired_at):
        """
        POST a layer upload URL request (all fields mandatory).

        Args:
            field_id (str): The ID of the field.
            layer_type_id (str): The layer type ID.
            acquired_at (str): Acquisition timestamp (ISO8601, e.g., 2025-11-21T10:15:30Z).
        Returns:
            Formatted response (DataFrame or dict) depending on self.output_format.
        """
        endpoint = "layers/upload-url"

        # Build JSON payload (all mandatory)
        payload = {
            "field_id": field_id,
            "layer_type_id": layer_type_id,
            "acquired_at": acquired_at
        }

        # Send POST request
        data = self._post(endpoint, payload=payload)
        return data
    
    def layers_rasters(self, layer_id):
        """
        Not yet available
        """
        endpoint = f"layers/{layer_id}/raster"
        data = self._get(endpoint)
        return data

    def layer_create(self, field_id, type_id, acquired_at, file_path):
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
        data = {"acquired_at": acquired_at, "type_id": type_id}

        try:
            response = self._post(endpoint, payload=data, files=files)
        finally:
            files["file"][1].close()  # close the file handle (index 1 in tuple)

        return response
