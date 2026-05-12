class ObservationsParameters:
    def observations_parameters(self, lang=None, page=None, limit=None):
        """
        Get all observation parameters.

        Args:
            lang (str, optional): Language code.
            page (int, optional): Page number (default 1).
            limit (int, optional): Results per page.

        Returns:
            list or DataFrame: Observation parameters with unit info.
        """
        endpoint = "observation-parameters"
        params = {}
        if lang:
            params["lang"] = lang
        if page:
            params["page"] = page
        if limit:
            params["limit"] = limit
        data = self._get(endpoint, params=params)
        return self._format_output(data)
