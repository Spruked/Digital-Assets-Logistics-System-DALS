# auto_worker_generation.py

class AutoWorkerGenerator:
    def __init__(self):
        self.clone_pool = [f"P-{i:03d}" for i in range(1, 11)]

    def generate_worker(self, identity, vault_bundle, job_ticket):
        """Generate a new worker clone with specified parameters"""
        if not self.clone_pool:
            raise ValueError("No available clones in pool")

        clone_id = self.clone_pool.pop(0)
        worker = {
            "id": clone_id,
            "identity": identity,
            "vault_bundle": vault_bundle,
            "job_ticket": job_ticket,
            "status": "active"
        }
        return worker

    def destroy_worker(self, worker_id):
        """Return worker to pool"""
        if worker_id not in self.clone_pool:
            self.clone_pool.append(worker_id)