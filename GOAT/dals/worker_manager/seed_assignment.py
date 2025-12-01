# seed_assignment.py

class SeedAssigner:
    def assign_seed(self, worker, vault_bundle):
        """Assign vault bundle to worker"""
        worker["vault_bundle"] = vault_bundle
        return worker