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
