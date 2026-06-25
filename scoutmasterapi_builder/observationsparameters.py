import pandas as pd
import requests

from .base import conceptual_class


@conceptual_class
class ObservationsParameters:
    def observations_parameters(self, page=None, limit=None, order=None, lang=None):
        """
        Get observation parameters.
        Args:
            page (int, optional): Page number (default 1).
            limit (int, optional): Results per page.
            order (str, optional): 'asc' or 'desc'.
            lang (str, optional): Language code ('en', 'nl', 'de', 'fr').
        Returns:
            pd.DataFrame or list: Observation parameters.
        """
        endpoint = "observation-parameters"
        params = {}
        if page: params["page"] = page
        if limit: params["limit"] = limit
        if order: params["order"] = order
        if lang: params["lang"] = lang
        data = self._get(endpoint, params=params)
        return self._format_output(data)
    
