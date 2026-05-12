import pandas as pd


class Cultivations:
    def cultivations(self, project_id):
        """
        Get all cultivation types that are practised within the project.
        Args:
            project_id (str): The ID of the project
        Returns:
            pd.DataFrame or list: Cultivations as DataFrame or JSON list.
        """
        endpoint = f"projects/{project_id}/calendars"
        params = {}
        if self.output_format in ["geojson", "gdf"]:
            params["output"] = "geojson"

        # Pass params to _get
        data = self._get(endpoint, params=params)
        return self._format_output(data)
    
    def cultivations_by_field(self, field_id):
        """
        Get all cultivations carried out on the field.
        Args:
            field_id (str): The ID of the field
        Returns:
            pd.DataFrame or list: Cultivations as DataFrame or JSON list.
        """
        endpoint = f"fields/{field_id}/calendars"
        params = {}
        if self.output_format in ["geojson", "gdf"]:
            params["output"] = "geojson"

        # Pass params to _get
        data = self._get(endpoint, params=params)
        return self._format_output(data)

    def cultivations_create(self, field_id, cultivation_data):
        """
        Create a new cultivation on the specified field.
        Args:        
            field_id (str): The ID of the field
            cultivation_data: specification of the intended cultivation
        Returns:
            pd.DataFrame or dict: Created cultivation.
        """        
        endpoint = f"fields/{field_id}/calendars"
        data = self._post(endpoint, cultivation_data)
        return self._format_output(data)
    
    def cultivations_tsum(self, cultivation_id):
        """
        Get data on the given cultivation - including tsum values
        Args:
            cultivation_id (str): The ID of the cultivation
        Returns:
            pd.DataFrame or list: DataFrame or JSON list with data on the given cultivation
        """
        endpoint = f"calendars/{cultivation_id}/tsum"
        data = self._get(endpoint)
        if self.output_format == "json":
            return data
        elif self.output_format == "df":
            # Convert the 'tsum' list of dicts into a DataFrame
            if len(data) == 0 or len(data["tsum"]) == 0: return pd.DataFrame()
            df = pd.DataFrame(data['tsum'])

            # Optional: convert 'date' to datetime
            df['date'] = pd.to_datetime(df['date'])

            # Optional: add crop info as columns for context
            df['crop_name'] = data['crop']['name']
            df['variety_name'] = data['crop']['variety_name']
            df['field_id'] = data['field_id']
            
            return df

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
        if crop_code is not None: payload["crop_code"] = crop_code
        if crop_variety_code is not None: payload["crop_variety_code"] = crop_variety_code
        if events is not None: payload["events"] = events
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

