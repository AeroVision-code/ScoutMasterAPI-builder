from .base import conceptual_class


@conceptual_class
class Researches:
    def researches(self, environment_id, page=None, limit=None, order=None,
                   sort_by=None, connected=None):
        """
        Get all researches for an environment.
        Args:
            environment_id (str): Environment to list researches for (required).
            page (int, optional): Page number (default 1).
            limit (int, optional): Results per page. Omit to return all.
            order (str, optional): 'asc' or 'desc'.
            sort_by (str, optional): 'id', 'recipient_nr' or 'research_nr'.
            connected (bool, optional): Filter by connected researches.
        Returns:
            pd.DataFrame or list: Researches as DataFrame or JSON list.
        """
        endpoint = "researches"
        params = {"environment_id": environment_id}
        if page: params["page"] = page
        if limit: params["limit"] = limit
        if order: params["order"] = order
        if sort_by: params["sort_by"] = sort_by
        if connected is not None: params["connected"] = connected
        data = self._get(endpoint, params=params)
        return self._format_output(data)

    def research_reprocess(self, research_id):
        """
        Reprocess a research by re-triggering its processing pipeline.
        Args:
            research_id (int): Numeric research ID.
        Returns:
            None (202 Accepted).
        """
        endpoint = f"researches/{research_id}/reprocess"
        return self._post(endpoint)
