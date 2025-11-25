class Layers:
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
        return self._format_output(data)
    
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
        self._check_auth()
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
