import requests
import mimetypes
import os.path
import datetime
import pandas as pd

from .base import conceptual

class Projects:
    def projects(self, page=None, limit=None, order=None, lang=None, sort_by=None):
        """
        Get data on all projects.
        Args:
            page (int, optional): Page number (default 1).
            limit (int, optional): Results per page. Omit to return all.
            order (str, optional): 'asc' or 'desc'.
            lang (str, optional): Language code ('en', 'nl', 'de', 'fr').
            sort_by (str, optional): 'name', 'created_at' or 'updated_at'.
        Returns:
            pd.DataFrame or list: DataFrame or JSON list with data on all
            projects as DataFrame.
        """
        try:
            endpoint = "projects/"
            params = {}
            if page: params["page"] = page
            if limit: params["limit"] = limit
            if order: params["order"] = order
            if lang: params["lang"] = lang
            if sort_by: params["sort_by"] = sort_by
            data = self._get(endpoint, params=params)
            return self._format_output(data)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")

    def project_create(self, user_id, name, abbreviation=None, environment_id=None,
                       description=None):
        """
        Create new project.

        Args:
            user_id (str): User ID of the creator (must be a project member).
            name (str): Project name.
            abbreviation (str, optional): Defaults to first 2 chars of name.
            environment_id (str): Environment the project belongs to. Required by
                the API; must reference an existing environment.
            description (str, optional): Project description.

        Returns:
            pd.DataFrame or dict: Created project as DataFrame or JSON.
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
            if environment_id is not None:
                project_data["environment_id"] = environment_id
            if description is not None:
                project_data["description"] = description
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

    @conceptual
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

