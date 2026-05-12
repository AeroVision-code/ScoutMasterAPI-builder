import mimetypes
import os


class Reports:
    def reports(self, project_id):
        """
        List all reports for a project.

        Args:
            project_id (str): UUID of the project.

        Returns:
            DataFrame or dict: Paginated list of reports.
        """
        endpoint = f"projects/{project_id}/reports"
        data = self._get(endpoint)
        return self._format_output(data)

    def report_create(self, project_id, title, user_id, file_path):
        """
        Upload a new report (PDF/file) to a project.

        Args:
            project_id (str): UUID of the project.
            title (str): Report title.
            user_id (str): UUID of the user uploading the report.
            file_path (str): Local path to the report file.

        Returns:
            dict: Created report data.
        """
        endpoint = f"projects/{project_id}/reports"

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type = "application/octet-stream"

        files = {
            "file": (
                os.path.basename(file_path),
                open(file_path, "rb"),
                mime_type,
            )
        }
        payload = {"title": title, "userId": user_id}

        try:
            response = self._post(endpoint, payload=payload, files=files)
        finally:
            files["file"][1].close()

        return response

    def report_update(self, report_id, title):
        """
        Update the title of a report.

        Args:
            report_id (str): UUID of the report.
            title (str): New title for the report.

        Returns:
            dict: Updated report data.
        """
        endpoint = f"reports/{report_id}"
        data = self._patch(endpoint, {"title": title})
        return data

    def report_delete(self, report_id):
        """
        Delete a report by ID.

        Args:
            report_id (str): UUID of the report.

        Returns:
            dict: Deleted report metadata.
        """
        endpoint = f"reports/{report_id}"
        data = self._delete(endpoint)
        return data

    def report_reference_add(self, report_id, ref_id, ref_type):
        """
        Add a reference (field or observation) to a report.

        Args:
            report_id (str): UUID of the report.
            ref_id (str): UUID of the referenced entity.
            ref_type (str): Either 'field' or 'observation'.

        Returns:
            dict: Created reference data.
        """
        if ref_type not in ("field", "observation"):
            raise ValueError("ref_type must be 'field' or 'observation'")
        endpoint = f"reports/{report_id}/references"
        data = self._post(endpoint, {"ref_id": ref_id, "ref_type": ref_type})
        return data

    def report_references(self, report_id):
        """
        List all references attached to a report.

        Args:
            report_id (str): UUID of the report.

        Returns:
            list or DataFrame: References for the report.
        """
        endpoint = f"reports/{report_id}/references"
        data = self._get(endpoint)
        return self._format_output(data)

    def report_reference_delete(self, reference_id):
        """
        Delete a report reference by its numeric ID.

        Args:
            reference_id (int): Numeric ID of the reference.

        Returns:
            dict: Deleted reference data or error.
        """
        endpoint = f"references/{reference_id}"
        data = self._delete(endpoint)
        return data
