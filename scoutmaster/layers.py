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