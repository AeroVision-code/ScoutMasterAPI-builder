class Crops:    
    def crops(self, sort_by=None, order=None, limit=None, page=None, lang=None, verbose=False):
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
        if lang:
            params["lang"] = lang

        data = self._get(endpoint, params=params, verbose=verbose)
        return self._format_output(data)
    
    def crop_varieties(self, crop_code, sort_by=None, order=None, limit=None, page=None):
        endpoint = f"crops/{crop_code}/varieties"
        params = {}
        if sort_by:
            params["sort_by"] = sort_by
        if order:
            params["order"] = order
        if limit:
            params["limit"] = limit
        if page:
            params["page"] = page
            
        data = self._get(endpoint, params=params)    
        
        return self._format_output(data)