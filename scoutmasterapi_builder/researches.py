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
        data = self._get_paged(endpoint, params=params)
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

    def research_by_id(self, research_id):
        """
        Get a research, including the reports holding its lab PDFs (report_ids).
        Args:
            research_id (int): Numeric research ID.
        Returns:
            dict: Research data.
        """
        endpoint = f"researches/{research_id}"
        data = self._get(endpoint)
        return data

    def research_create(self, research_nr, observation_id, recipient_nr=None,
                        reference_code=None, research_category_id=None, report_id=None):
        """
        Save a research (lab order number) for an observation created from an
        uploaded report. An existing research with the same recipient_nr +
        research_nr is linked instead of duplicated.
        Args:
            research_nr (str): Lab order/research number as printed on the report.
            observation_id (str): Observation the measurements were saved to.
            recipient_nr (int, optional): Lab client number (from report validation).
            reference_code (str, optional): Reference code.
            research_category_id (int, optional): Research category ID.
            report_id (str, optional): Report the source file was uploaded as.
        Returns:
            dict: Created (or linked) research.
        """
        endpoint = "researches"
        payload = {"research_nr": research_nr, "observation_id": observation_id}
        if recipient_nr is not None: payload["recipient_nr"] = recipient_nr
        if reference_code is not None: payload["reference_code"] = reference_code
        if research_category_id is not None: payload["research_category_id"] = research_category_id
        if report_id is not None: payload["report_id"] = report_id
        data = self._post(endpoint, payload)
        return data

    def research_report_add(self, research_id, report_id):
        """
        Link a report holding (one of) this research's lab PDFs.
        Linking an already linked report changes nothing.
        Args:
            research_id (int): Numeric research ID.
            report_id (str): UUID of the report.
        Returns:
            dict: Updated research.
        """
        endpoint = f"researches/{research_id}/reports"
        data = self._post(endpoint, {"report_id": report_id})
        return data

    def research_report_remove(self, research_id, report_id):
        """
        Remove the link between a research and a report. The report itself stays.
        Args:
            research_id (int): Numeric research ID.
            report_id (str): UUID of the report.
        Returns:
            dict: Updated research.
        """
        endpoint = f"researches/{research_id}/reports/{report_id}"
        data = self._delete(endpoint)
        return data
