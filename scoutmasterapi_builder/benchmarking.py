class Benchmarking:
    def benchmark(self, peergroup_cultivation_ids, reference_cultivation_id=None):
        """
        Benchmark cultivations against a peer group using WDVI layer statistics,
        aligned by day-delta from plant date.

        Only cultivations that have a plant date and at least one WDVI layer
        will contribute to the aggregate.

        Args:
            peergroup_cultivation_ids (list[str]): Cultivation IDs to include in the peer group.
            reference_cultivation_id (str, optional): Cultivation ID to use as the reference line.
        Returns:
            dict: Benchmark result containing:
                - layer_type: dict with 'id' and 'name'
                - peergroup: list of PeergroupEntry dicts
                - benchmark_data: list of BenchmarkDataPoint dicts with
                  day_delta, mean, std, field_count, field_reference
        """
        payload = {"peergroup_cultivation_ids": peergroup_cultivation_ids}
        if reference_cultivation_id:
            payload["reference_cultivation_id"] = reference_cultivation_id
        data = self._post("benchmark", payload)
        return data
