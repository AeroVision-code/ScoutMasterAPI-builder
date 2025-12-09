import pandas as pd
import requests
import mimetypes

class Projects:
    def projects(self):
        data = self._get("projects/")
        return self._format_output(data)
    
    def project_create(self, user_id, name, abbreviation=None):

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
        if abbreviation is None:
            abbreviation = name[:2].upper()
        project_data = {"user_id": user_id,
                  "name": name,
                  "abbreviation": abbreviation}
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        try:
            response = requests.post(endpoint, json=project_data, headers=headers)
            response_json = response.json()
            if response.status_code == 200 or response.status_code == 201:
                return pd.DataFrame(response_json) if self.output_format == "df" else response_json
            else:
                raise Exception(f"Failed to create fields: {response.status_code} {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")
        
    def upload_project_logo(self, project_id, file_path):
        """
        Upload a logo file for a specific project.
        
        Steps:
        1. Request presigned URL from API
        2. Upload file to S3 using PUT
        3. Return final metadata result from API if needed
        """
        self._check_auth()

        # 1️⃣ Request presigned URL
        endpoint = f"{self.host}projects/{project_id}/logo/upload-url"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }

        presign_res = requests.get(endpoint, headers=headers)

        if presign_res.status_code != 200:
            raise Exception(f"Error getting upload URL: {presign_res.status_code} {presign_res.text}")

        presign_data = presign_res.json()
        upload_url = presign_data["upload_url"]
        public_url = presign_data["public_url"]
        file_key = presign_data["file_key"]

        # 2️⃣ Upload file directly to S3 using PUT
    
        mime_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"

        with open(file_path, "rb") as file:
            upload_res = requests.put(upload_url, data=file, headers={"Content-Type": mime_type})

        if upload_res.status_code not in (200, 201):
            raise Exception(f"S3 upload failed: {upload_res.status_code} {upload_res.text}")

        print("Logo uploaded successfully!")

        # 3️⃣ Return metadata including final public URL
        return {
            "project_id": project_id,
            "file_key": file_key,
            "public_url": public_url
        }

        
