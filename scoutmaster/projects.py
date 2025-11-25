import pandas as pd
import requests

class Projects:
    def projects(self):
        data = self._get("projects/")
        return self._format_output(data)
    
    def project_create(self, project_data, userid, client_id=None):

        """
        Create new project

        Args:
            project_collection_id (str): The ID of the project collection.
            fields_data (list): List of field dicts to create.

        Returns:
            pd.DataFrame or dict: Created fields as DataFrame or JSON.
        """
        self._check_auth()
        endpoint = f"{self.host}projects"
        params = {"user_id": userid}
        if client_id is not None:
            params["client_id"] = client_id
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        try:
            response = requests.post(endpoint, json=project_data, headers=headers, params=params)
            response_json = response.json()
            if response.status_code == 200 or response.status_code == 201:
                return pd.DataFrame(response_json) if self.output_format == "df" else response_json
            else:
                raise Exception(f"Failed to create fields: {response.status_code} {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")
        
