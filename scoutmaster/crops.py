class Crops:    
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