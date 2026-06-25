import mimetypes
import os

from .base import conceptual_class


@conceptual_class
class Services:
    def services(self, lang=None):
        """
        Get all services (admin only).
        Args:
            lang (str, optional): Language code.
        Returns:
            list or DataFrame: Available services.
        """
        endpoint = "services"
        params = {}
        if lang: params["lang"] = lang
        data = self._get(endpoint, params=params)
        return self._format_output(data)

    def services_by_project(self, project_id, lang=None):
        """
        Get the services enabled for a project.
        Args:
            project_id (str): UUID of the project.
            lang (str, optional): Language code.
        Returns:
            list or DataFrame: Services for the project.
        """
        endpoint = f"projects/{project_id}/services"
        params = {}
        if lang: params["lang"] = lang
        data = self._get(endpoint, params=params)
        return self._format_output(data)

    def services_create(self, project_id, service_id):
        """
        Enable a service for a project (admin only).
        Args:
            project_id (str): UUID of the project.
            service_id (int): Numeric ID of the service.
        Returns:
            list or dict: Updated list of project services.
        """
        endpoint = f"projects/{project_id}/services/{service_id}"
        data = self._post(endpoint)
        return data

    def services_delete(self, project_id, service_id):
        """
        Remove a service from a project (admin only).
        Args:
            project_id (str): UUID of the project.
            service_id (int): Numeric ID of the service.
        Returns:
            list or dict: Updated list of project services.
        """
        endpoint = f"projects/{project_id}/services/{service_id}"
        data = self._delete(endpoint)
        return data


@conceptual_class
class ResearchCategories:
    def research_categories(self, page=None, limit=None, order=None, sort_by=None):
        """
        Get all research categories.
        Args:
            page (int, optional): Page number (default 1).
            limit (int, optional): Results per page.
            order (str, optional): 'asc' or 'desc'.
            sort_by (str, optional): 'created_at' or 'updated_at'.
        Returns:
            list or DataFrame: Research categories.
        """
        endpoint = "research-categories"
        params = {}
        if page: params["page"] = page
        if limit: params["limit"] = limit
        if order: params["order"] = order
        if sort_by: params["sort_by"] = sort_by
        data = self._get(endpoint, params=params)
        return self._format_output(data)

    def validate_report(self, research_category_id, file_path):
        """
        Validate that a PDF matches the expected format for a research category.
        Args:
            research_category_id (int): Numeric research category ID.
            file_path (str): Local path to the PDF to validate.
        Returns:
            dict: ReportValidationResult (valid, category, reason, data).
        """
        self._check_auth()
        endpoint = f"research-categories/{research_category_id}/reports/validate"
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type = "application/octet-stream"
        with open(file_path, "rb") as fh:
            files = {"file": (os.path.basename(file_path), fh, mime_type)}
            return self._post(endpoint, files=files)
