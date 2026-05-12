import pandas as pd


class Cultivations:
    def cultivations(self, project_id, page=None, limit=None, order=None, lang=None, sort_by=None):
        """
        Get all cultivation calendars for a project.

        Args:
            project_id (str): UUID of the project.
            page (int, optional): Page number (default 1).
            limit (int, optional): Results per page.
            order (str, optional): 'asc' or 'desc'.
            lang (str, optional): Language code.
            sort_by (str, optional): 'created_at' or 'updated_at'.

        Returns:
            DataFrame or dict: Paginated cultivation calendars.
        """
        endpoint = f"projects/{project_id}/calendars"
        params = {}
        if page:
            params["page"] = page
        if limit:
            params["limit"] = limit
        if order:
            params["order"] = order
        if lang:
            params["lang"] = lang
        if sort_by:
            params["sort_by"] = sort_by
        data = self._get(endpoint, params=params)
        return self._format_output(data)

    def cultivations_by_field(self, field_id, lang=None):
        """
        Get all cultivation calendars for a field.

        Args:
            field_id (str): UUID of the field.
            lang (str, optional): Language code.

        Returns:
            list or DataFrame: Cultivation calendars for the field.
        """
        endpoint = f"fields/{field_id}/calendars"
        params = {}
        if lang:
            params["lang"] = lang
        data = self._get(endpoint, params=params)
        return self._format_output(data)

    def cultivations_create(self, field_id, cultivation_data):
        """
        Create a cultivation calendar for a field.

        Args:
            field_id (str): UUID of the field.
            cultivation_data (dict): Must include crop_code, crop_variety_code, and events.

        Returns:
            dict: Created cultivation calendar.
        """
        endpoint = f"fields/{field_id}/calendars"
        data = self._post(endpoint, cultivation_data)
        return self._format_output(data)

    def cultivation_update(self, calendar_id, crop_code=None, crop_variety_code=None, events=None):
        """
        Update a cultivation calendar.

        Args:
            calendar_id (str): ID of the cultivation calendar.
            crop_code (int, optional): Updated crop code.
            crop_variety_code (int, optional): Updated crop variety code.
            events (list, optional): Updated list of event dicts with 'type' and 'date'.

        Returns:
            dict: Updated cultivation calendar.
        """
        endpoint = f"calendars/{calendar_id}"
        payload = {}
        if crop_code is not None:
            payload["crop_code"] = crop_code
        if crop_variety_code is not None:
            payload["crop_variety_code"] = crop_variety_code
        if events is not None:
            payload["events"] = events
        data = self._patch(endpoint, payload)
        return data

    def cultivation_delete(self, calendar_id):
        """
        Delete a cultivation calendar.

        Args:
            calendar_id (str): ID of the cultivation calendar.

        Returns:
            None (204 No Content).
        """
        endpoint = f"calendars/{calendar_id}"
        self._delete(endpoint)

    def cultivations_tsum(self, cultivation_id):
        """
        Get TSUM data for a cultivation calendar.

        Args:
            cultivation_id (str): ID of the cultivation calendar.

        Returns:
            dict or DataFrame: TSUM data.
        """
        endpoint = f"calendars/{cultivation_id}/tsum"
        data = self._get(endpoint)
        if self.output_format == "json":
            return data
        elif self.output_format == "df":
            df = pd.DataFrame(data["tsum"])
            df["date"] = pd.to_datetime(df["date"])
            df["crop_name"] = data["crop"]["name"]
            df["variety_name"] = data["crop"]["variety_name"]
            df["field_id"] = data["field_id"]
            return df
