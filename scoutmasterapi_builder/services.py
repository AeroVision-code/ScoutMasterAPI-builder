class Services:
    def services_by_project(self, project_id):
        endpoint = f"projects/{project_id}/services"
        data = self._get(endpoint)
        return self._format_output(data)
    
    def services_create(self, project_id, service_id):
        endpoint = f"projects/{project_id}/services/{service_id}"
        raise NotImplementedError("Adding subscriptions is not yet implemented!")