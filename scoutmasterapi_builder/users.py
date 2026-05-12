import requests

class Users:    
    def users(self, project_id):
        """
        Get all users who have access to the project.
        Args:
            project_id (str): The ID of the project
        Returns:
            pd.DataFrame or list: Users as DataFrame or JSON list.
        """
        endpoint = f"projects/{project_id}/users"
        params = {}
        if self.output_format in ["geojson", "gdf"]:
            params["output"] = "geojson"

        # Pass params to _get
        data = self._get(endpoint, params=params)
        return self._format_output(data)
    
    def user_invite(self, project_id, email, role="member"):
        """
        Invites a new user
        Args:
            project_id (str): the ID of the project 
            email (str): the email address of the invited person
            role (str): the intended role of the invited person
        Returns:
            pd.DataFrame or dict: Created invitation as DataFrame or JSON.
        """
        try:
            endpoint = f"projects/{project_id}/invites"
            message = f"Dit is een uitnodiging die is verstuurd vanaf het ScoutMaster platform."
            user_data = {"email": email, "role": role, "message": message}
            data = self._post(endpoint, user_data)
            return data

        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")
        
    def user_validates(self, token):
        """
        The user can validate the token sent with the invitation
        Args:
        
        Returns:
            pd.DataFrame or dict: valid / non-valid as DataFrame or JSON list.
        """
        endpoint = f"invites/{token}/validate"
        data = self._get(endpoint)
        data["project"] = data["project"]["name"]
        if self.output_format == "df":
            data = {k: [v] for k, v in data.items()}
        return self._format_output(data)
        
    def user_accepts(self, token):
        """
        The user can accept the invitation using the token - different from invite_id
        Args:
            token (str): the token sent with the invitation
        Returns:
            pd.DataFrame or dict: user data as DataFrame or JSON list.
        """
        endpoint = f"invites/{token}/accept"
        data = self._post(endpoint)
        if self.output_format == "df":
            data = {k: [v] for k, v in data.items()}
            
        # TODO: authentication is required via the frontend
        return self._format_output(data)
    
    
