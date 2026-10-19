import os.path
import pandas as pd
import requests


class Fields:
    def fields(self, project_id, page=None, limit=None, order=None, lang=None, sort_by=None, crs=None):
        """
        Get all the fields that are used within the specified project.
        Args:
            project_id (str): The ID of the project
            page (int, optional): Page number (default 1).
            limit (int, optional): Results per page. Omit to return all.
            order (str, optional): 'asc' or 'desc'.
            lang (str, optional): Language for field labels.
            sort_by (str, optional): 'name', 'created_at' or 'updated_at'.
            crs (int, optional): Output CRS EPSG code (default 4326).
        Returns:
            pd.DataFrame or list: Fields as DataFrame or JSON list.
        """
        endpoint = f"projects/{project_id}/fields"
        params = {}
        if page: params["page"] = page
        if limit: params["limit"] = limit
        if order: params["order"] = order
        params["lang"] = lang or self.lang
        if sort_by: params["sort_by"] = sort_by
        if crs: params["crs"] = crs
        # spatial shaping is done client-side from the WKT geometry the regular
        # endpoint returns, so pagination is preserved. Use fields_geojson() for
        # the server's GeoJSON FeatureCollection.
        data = self._get_paged(endpoint, params=params)
        return self._format_output(data, crs=crs)

    def field_by_id(self, field_id, lang=None):
        """
        Get the field indicated by the given field ID.
        Args:
            field_id (str): The ID of the field
            lang (str, optional): Language for field labels; defaults to the client's lang.
        Returns:
            pd.DataFrame, GeoDataFrame, dict or GeoJSON depending on
            output_format.
        """
        endpoint = f"fields/{field_id}"
        data = self._get(endpoint, params={"lang": lang or self.lang})
        return self._format_output(data)

    def field_by_location(self, project_id, lat, lon, lang=None):
        """
        Get the field used within the specified project, filtered by the point location.
        Args:
            project_id (str): The ID of the project
            lat (float): the latitude of the point
            lon (float): the longitude of the point
            lang (str, optional): Language for field labels; defaults to the client's lang.
        Returns:
            pd.DataFrame, GeoDataFrame, dict or GeoJSON depending on
            output_format.
        """
        # No GeoJSON variant for by-location; the regular response carries WKT
        # geometry which _format_output parses when spatial is set.
        endpoint = f"projects/{project_id}/fields/by-location"
        params = {"lat": lat, "long": lon, "lang": lang or self.lang}
        data = self._get(endpoint, params=params)
        return self._format_output(data)
        
    def fields_create(self, project_id, field_data):
        """
        Create a new field in the specified project.
        Args:
            project_id (str): The ID of the project.
            field_data (dict): Field data with required fields:
                {
                    "user_id": "uuid",
                    "name": "string",
                    "properties": {
                        "description": "string"
                    },
                    "geometry": { "type": "Polygon", "coordinates": [[x, y]] },
                }
        Returns:
            pd.DataFrame or dict: Created field.
        """
        endpoint = f"projects/{project_id}/fields"
        try:
            data = self._post(endpoint, field_data)
            return self._format_output(data)

        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")

    def field_update(self, field_id, name=None, geometry=None, lang=None):
        """
        Update a field name and/or geometry.
        Args:
            field_id (str): UUID of the field.
            name (str, optional): New field name.
            geometry (dict or str, optional): New geometry as GeoJSON dict or WKT string.
            lang (str, optional): Language for labels in the response; defaults to the client's lang.
        Returns:
            dict: Updated field data with message.
        """
        endpoint = f"fields/{field_id}"
        payload = {}
        if name is not None: payload["name"] = name
        if geometry is not None: payload["geometry"] = geometry
        data = self._patch(endpoint, payload, params={"lang": lang or self.lang})
        return data

    def field_delete(self, field_id):
        """
        Delete a field by ID.
        Args:
            field_id (str): UUID of the field.
        Returns:
            bool: True if the field was deleted successfully (204 No Content).
        """
        endpoint = f"fields/{field_id}"
        deleted = self._delete(endpoint)
        if deleted:
            self._log(f" > Field \033[94m{field_id}\033[0m deleted successfully.")
        return deleted

    # ── GeoJSON variants (not paginated; return a FeatureCollection) ─────────
    def fields_geojson(self, project_id, lang=None, sort_by=None, order=None, crs=None):
        """
        Get all fields of a project as a GeoJSON FeatureCollection.
        Args:
            project_id (str): UUID of the project.
            lang (str, optional): Language for field labels.
            sort_by (str, optional): 'name', 'created_at' or 'updated_at'.
            order (str, optional): 'asc' or 'desc'.
            crs (int, optional): Output CRS EPSG code (default 4326).
        Returns:
            GeoDataFrame, dict, or JSON depending on output_format.
        """
        endpoint = f"projects/{project_id}/fields/geojson"
        params = {}
        params["lang"] = lang or self.lang
        if sort_by: params["sort_by"] = sort_by
        if order: params["order"] = order
        if crs: params["crs"] = crs
        data = self._get(endpoint, params=params)
        return self._format_output(data, crs=crs)

    def field_by_id_geojson(self, field_id, lang=None, crs=None):
        """
        Get a single field as a GeoJSON FeatureCollection.
        Args:
            field_id (str): UUID of the field.
            lang (str, optional): Language for field labels.
            crs (int, optional): Output CRS EPSG code (default 4326).
        Returns:
            GeoDataFrame, dict, or JSON depending on output_format.
        """
        endpoint = f"fields/{field_id}/geojson"
        params = {}
        params["lang"] = lang or self.lang
        if crs: params["crs"] = crs
        data = self._get(endpoint, params=params)
        return self._format_output(data, crs=crs)

    # ── Machine-data uploads (currently: John Deere seeding shapefile .zip) ──
    def field_upload_url(self, field_id, filename=None):
        """
        Get a presigned direct-to-S3 upload URL for a machine-data file tied to
        a field. PUT the file to `upload_url` with Content-Type application/zip
        within ~5 minutes, then poll field_upload_job() with `job_id`.
        Args:
            field_id (str): UUID of the field.
            filename (str, optional): Original filename, stored with the file.
        Returns:
            dict: {"upload_url": ..., "s3_key": ..., "job_id": ...}
        """
        endpoint = f"fields/{field_id}/upload-file"
        payload = {}
        if filename: payload["filename"] = filename
        data = self._post(endpoint, payload)
        return data

    def field_upload_file(self, field_id, file_path):
        """
        Upload a machine-data .zip for a field: presigns the URL, then PUTs the
        file straight to S3. Poll field_upload_job() with the returned job_id.
        Args:
            field_id (str): UUID of the field.
            file_path (str): Local path to the .zip file.
        Returns:
            dict: {"upload_url": ..., "s3_key": ..., "job_id": ...}
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        data = self.field_upload_url(field_id, filename=os.path.basename(file_path))
        # The URL is presigned for application/zip; S3 rejects any other type.
        self.upload_file(file_path, data["upload_url"], content_type="application/zip",
                         verbose=self.verbose)
        return data

    def field_upload_job(self, field_id, job_id):
        """
        Get the status of an upload job created by field_upload_url().
        Poll until status is DONE or FAILED; `result` carries the stage summary
        or, once FAILED, the reason.
        Args:
            field_id (str): UUID of the field.
            job_id (str): ID of the upload job.
        Returns:
            dict: Upload job (id, status, result, filename, created_at, expires_at).
        """
        endpoint = f"fields/{field_id}/upload-jobs/{job_id}"
        data = self._get(endpoint)
        return data

