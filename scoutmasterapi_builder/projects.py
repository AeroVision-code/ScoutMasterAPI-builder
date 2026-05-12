import requests
import mimetypes
import os.path
import datetime
import pandas as pd

class Projects:
    def projects(self):
        """
        Get data on all projects      
        Returns:
            pd.DataFrame or list: DataFrame or JSON list with data on all 
            projects as DataFrame.
        """
        try: 
            endpoint = "projects/"
            data = self._get(endpoint)
            return self._format_output(data)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")
    
    def project_create(self, user_id, name, abbreviation=None):
        """
        Create new project

        Args:
            project_collection_id (str): The ID of the project collection.
            fields_data (list): List of field dicts to create.

        Returns:
            pd.DataFrame or dict: Created fields as DataFrame or JSON.
        """
        try:
            endpoint = f"projects"
            if abbreviation is None:
                abbreviation = name[:2].upper()
                
            project_data = {
                "user_id": user_id,
                "name": name,
                "abbreviation": abbreviation
            }
            data = self._post(endpoint, project_data)
            return data

        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")
        
    def project_by_id(self, project_id):
        """
        Get data on the given project
        Args:
            project_id (str): The ID of the project
        Returns:
            pd.DataFrame or list: DataFrame or JSON list with data on the 
            project in the form of a DataFrame
        """
        try:
            endpoint = f"projects/{project_id}"
            data = self._get(endpoint)
            return data
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")
        
    def project_upload_logo(self, project_id: str, file_path: str):
        """
        POST a layer upload URL request (all fields mandatory).

        Args:
            field_id (str): The ID of the field.
            layer_type_id (str): The layer type ID.
            acquired_at (str): Acquisition timestamp (ISO8601, e.g., 2025-11-21T10:15:30Z).

        Returns:
            Formatted response (DataFrame or dict) depending on self.output_format.
        """
        # Initialise
        if self.output_format == "df": response = pd.DataFrame()
        else: response = {}
        self._check_auth()
        endpoint = f"projects/{project_id}/logo"
        
        # Check input
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Detect mimetype from file extension
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type = 'application/octet-stream'

        # Prepare some extra data
        dt_now = datetime.datetime.now(datetime.UTC)
        data = {"acquired_at": dt_now.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"}

        # Explicitly set filename and content type before posting the file content
        with open(file_path, "rb") as fh:
            files = {
                "file": (
                    os.path.basename(file_path), # filename
                    fh,                          # file handle
                    mime_type,                   # content type
                )
            }
            response = self._post(endpoint, payload=data, files=files)
        return response

    def project_update(self, project_id, name, abbreviation=None):
        """
        Update a project name and abbreviation.
        Args:
            project_id (str): UUID of the project.
            name (str): New project name.
            abbreviation (str, optional): New abbreviation. Defaults to first 2 chars of name.
        Returns:
            dict: Updated project data.
        """
        if abbreviation is None:
            abbreviation = name[:2].upper()
        endpoint = f"projects/{project_id}"
        data = self._patch(endpoint, {"name": name, "abbreviation": abbreviation})
        return data

    def update_user_role(self, project_id, user_id, role):
        """
        Update the role of a user within a project.
        Args:
            project_id (str): UUID of the project.
            user_id (str): ID of the user.
            role (str): New role — 'member' or 'owner'.
        Returns:
            dict: Contains role, project_id, user_id and message.
        """
        if role not in ("member", "owner"):
            raise ValueError("role must be 'member' or 'owner'")
        endpoint = f"projects/{project_id}/users/{user_id}/role"
        data = self._patch(endpoint, {"role": role})
        return data

