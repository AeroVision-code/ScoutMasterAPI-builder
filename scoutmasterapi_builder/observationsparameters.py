import pandas as pd
import requests


class ObservationsParameters:
    def observations_parameters(self):
        endpoint = f"observation-parameters"

        # Pass params to _get
        data = self._get(endpoint)
        return self._format_output(data)
    
