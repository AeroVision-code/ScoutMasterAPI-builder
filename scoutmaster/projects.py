import requests
import mimetypes


class Projects:
    def projects(self):
        try:
            endpoint = "projects/"
            data = self._get(endpoint)
            return self._format_output(data)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")

    def project_create(self, user_id, name, abbreviation=None):
        """
        Create a new project.

        Args:
            user_id (str): UUID of the creating user.
            name (str): Project name.
            abbreviation (str, optional): Abbreviation. Defaults to first 2 chars of name.

        Returns:
            dict: Created project data.
        """
        try:
            endpoint = "projects"
            if abbreviation is None:
                abbreviation = name[:2].upper()
            project_data = {
                "user_id": user_id,
                "name": name,
                "abbreviation": abbreviation,
            }
            data = self._post(endpoint, project_data)
            return data
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")

    def project_by_id(self, project_id):
        """
        Get a project by its UUID.

        Args:
            project_id (str): UUID of the project.

        Returns:
            dict: Project data.
        """
        try:
            endpoint = f"projects/{project_id}"
            data = self._get(endpoint)
            return data
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")

    def project_update(self, project_id, name, abbreviation=None):
        """
        Update a project's name and abbreviation.

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
        payload = {"name": name, "abbreviation": abbreviation}
        data = self._patch(endpoint, payload)
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

    def project_uploadurl(self, project_id):
        """Request a presigned upload URL for a project logo."""
        self._check_auth()
        endpoint = f"projects/{project_id}/logo/upload-url"
        data = self._post(endpoint)
        return data

    def project_upload_logo(self, project_id, file_path):
        """
        Upload a logo file for a specific project via presigned URL.

        Args:
            project_id (str): UUID of the project.
            file_path (str): Local path to the logo file.

        Returns:
            dict: Contains project_id, file_key and public_url.
        """
        self._check_auth()
        endpoint = f"projects/{project_id}/logo/upload-url"
        try:
            presign_data = self._post(endpoint)
            upload_url = presign_data["upload_url"]
            public_url = presign_data["public_url"]
            file_key = presign_data["file_key"]
            mime_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
            with open(file_path, "rb") as file:
                upload_res = requests.put(
                    upload_url, data=file, headers={"Content-Type": mime_type}
                )
            if upload_res.status_code not in (200, 201):
                raise Exception(
                    f"S3 upload failed: {upload_res.status_code} {upload_res.text}"
                )
            return {"project_id": project_id, "file_key": file_key, "public_url": public_url}
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")
