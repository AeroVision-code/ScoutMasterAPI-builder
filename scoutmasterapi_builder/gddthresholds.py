class GddThresholds:
    """Tsum (growing degree days) base/upper temperatures per crop or variety."""

    def gdd_thresholds(self):
        """
        Get all crops and varieties that have their own tbase/tupper.
        Returns:
            pd.DataFrame or list: Tsum thresholds.
        """
        data = self._get("gdd-thresholds")
        return self._format_output(data)

    def crop_gdd_threshold_set(self, crop_code, tbase, tupper):
        """
        Set tbase/tupper for a whole crop (all its varieties without their own
        values). Creates the values or replaces existing ones.
        Args:
            crop_code (int): Crop code.
            tbase (float): Base temperature in °C. Must be lower than tupper.
            tupper (float): Upper temperature cap in °C.
        Returns:
            dict: The crop's thresholds.
        """
        endpoint = f"crops/{crop_code}/gdd-threshold"
        data = self._put(endpoint, {"tbase": float(tbase), "tupper": float(tupper)})
        return data

    def crop_gdd_threshold_delete(self, crop_code):
        """
        Remove a crop's own tbase/tupper; its cultivations fall back to the defaults.
        Args:
            crop_code (int): Crop code.
        Returns:
            bool: True on success (204 No Content).
        """
        endpoint = f"crops/{crop_code}/gdd-threshold"
        return self._delete(endpoint)

    def variety_gdd_threshold_set(self, crop_code, variety_code, tbase, tupper):
        """
        Set tbase/tupper for one variety; overrides the crop's values.
        Creates the values or replaces existing ones.
        Args:
            crop_code (int): Crop code.
            variety_code (int): Variety code.
            tbase (float): Base temperature in °C. Must be lower than tupper.
            tupper (float): Upper temperature cap in °C.
        Returns:
            dict: The variety's thresholds.
        """
        endpoint = f"crops/{crop_code}/varieties/{variety_code}/gdd-threshold"
        data = self._put(endpoint, {"tbase": float(tbase), "tupper": float(tupper)})
        return data

    def variety_gdd_threshold_delete(self, crop_code, variety_code):
        """
        Remove a variety's own tbase/tupper; it falls back to the crop's values.
        Args:
            crop_code (int): Crop code.
            variety_code (int): Variety code.
        Returns:
            bool: True on success (204 No Content).
        """
        endpoint = f"crops/{crop_code}/varieties/{variety_code}/gdd-threshold"
        return self._delete(endpoint)
