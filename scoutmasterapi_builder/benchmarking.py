from .base import conceptual_class


@conceptual_class
class Benchmarking:
    def benchmark_peergroup(self, cultivation_ids, layer_type_id=None, x_axis=None):
        """
        Benchmark a peer group of cultivations.

        Fetches the selected layer statistics for the peer group, aligned by the
        chosen axis. Only cultivations with a plant date and at least one matching
        layer contribute to the aggregate. The reference line is a separate call
        (see benchmark_reference).

        Args:
            cultivation_ids (list[str]): Cultivation IDs to include in the peer group.
            layer_type_id (str, optional): Layer type to benchmark on. Falls back to WDVI.
            x_axis (str, optional): 'day_delta' (default) or 'tsum'.
        Returns:
            dict: PeergroupBenchmarkResponse (layer_type, x_axis, peergroup, benchmark_data).
        """
        payload = {"cultivation_ids": cultivation_ids}
        if layer_type_id: payload["layer_type_id"] = layer_type_id
        if x_axis: payload["x_axis"] = x_axis
        data = self._post("benchmark/peergroup", payload)
        return data

    def benchmark_reference(self, cultivation_id, layer_type_id=None, x_axis=None):
        """
        Compute a single cultivation's reference curve.

        Returns the cultivation's layer means aligned on the chosen axis. For the
        tsum axis the curve snaps to the same fixed grid the peer group uses, so
        the two series line up when overlaid.

        Args:
            cultivation_id (str): Cultivation ID to compute the reference line for.
            layer_type_id (str, optional): Layer type to benchmark on. Falls back to WDVI.
            x_axis (str, optional): 'day_delta' (default) or 'tsum'.
        Returns:
            dict: ReferenceCurveResponse (layer_type, x_axis, reference, data).
        """
        payload = {"cultivation_id": cultivation_id}
        if layer_type_id: payload["layer_type_id"] = layer_type_id
        if x_axis: payload["x_axis"] = x_axis
        data = self._post("benchmark/reference", payload)
        return data

    # Legacy alias — the old single /benchmark endpoint is now split in two.
    def benchmark(self, peergroup_cultivation_ids, reference_cultivation_id=None,
                  layer_type_id=None, x_axis=None):
        """Deprecated: use benchmark_peergroup() (and benchmark_reference()).

        Calls benchmark_peergroup; if reference_cultivation_id is given, also
        calls benchmark_reference and returns both under 'peergroup'/'reference'.
        """
        result = {"peergroup": self.benchmark_peergroup(
            peergroup_cultivation_ids, layer_type_id=layer_type_id, x_axis=x_axis)}
        if reference_cultivation_id:
            result["reference"] = self.benchmark_reference(
                reference_cultivation_id, layer_type_id=layer_type_id, x_axis=x_axis)
        return result
