"""
Micro-SKG ~ 180 lines
=====================
Fits inside any DALS worker (no deps except networkx)
Provides instant co-occurrence clustering and predicate invention

Usage:
    from micro_skg import MicroSKG
    
    skg = MicroSKG()
    clusters = skg.bootstrap(raw_text, user_id="u1", file_id="f1")
    pyvis_data = skg.to_pyvis_dict()
"""

import re
import uuid
import json
from collections import defaultdict
from typing import List, Dict, Any
import networkx as nx


class MicroSKG:
    """
    Lightweight semantic knowledge graph for edge workers
    
    Features:
    - Bootstrap raw text → nodes/edges
    - Density-based clustering
    - Predicate invention (co-occurrence)
    - NetworkX export for PyVis visualization
    """
    
    def __init__(self):
        self.G = nx.MultiDiGraph()
        self._stop = set("the a an of to in on for with at by from".split())

    # ---------- Public API ----------
    
    def bootstrap(self, raw: str, user_id: str = "", file_id: str = "") -> List[Dict[str, Any]]:
        """
        Bootstrap text into knowledge graph
        
        Args:
            raw: Raw text to process
            user_id: User identifier for provenance
            file_id: File identifier for provenance
        
        Returns:
            List of cluster dicts with id, seed, nodes, density
        """
        self._add_text_graph(raw)
        clusters = self._density_clusters()
        
        # Tag cluster membership in nodes
        for c in clusters:
            self.G.nodes[c["seed"]]["cluster"] = c["id"]
            self.G.nodes[c["seed"]]["user_id"] = user_id
            self.G.nodes[c["seed"]]["file_id"] = file_id
        
        return clusters

    def to_networkx(self) -> nx.MultiDiGraph:
        """Return underlying NetworkX graph"""
        return self.G

    def to_pyvis_dict(self) -> Dict[str, Any]:
        """
        Export to JSON-serializable dict for PyVis React component
        
        Returns:
            Dict with 'nodes' and 'edges' arrays
        """
        nodes = [
            {"id": n, "label": n, **self.G.nodes[n]}
            for n in self.G.nodes
        ]
        edges = [
            {"from": u, "to": v, **d}
            for u, v, k, d in self.G.edges(keys=True, data=True)
        ]
        return {"nodes": nodes, "edges": edges}

    # ---------- Internals ----------
    
    def _add_text_graph(self, text: str):
        """
        Build co-occurrence graph from sliding window
        
        Creates edges between words that appear within window_size of each other.
        Edge weights accumulate with repeated co-occurrences.
        """
        tokens = re.findall(r"\b\w+\b", text.lower())
        tokens = [t for t in tokens if t not in self._stop and len(t) > 2]
        
        window = 5  # sliding window size
        
        for i in range(len(tokens) - window):
            chunk = tokens[i : i + window]
            
            # Create edges for all pairs in window
            for a in chunk:
                for b in chunk:
                    if a != b:
                        if self.G.has_edge(a, b):
                            # Increment existing edge weight
                            self.G[a][b][0]["weight"] += 1
                        else:
                            # Create new edge
                            self.G.add_edge(
                                a, b,
                                weight=1,
                                predicate="co_occurs",
                                id=str(uuid.uuid4())
                            )

    def _density_clusters(self, w: int = 5) -> List[Dict[str, Any]]:
        """
        Greedy w-core clustering → density = 2|E|/|V|(|V|-1)
        
        Args:
            w: Minimum edge weight for core membership
        
        Returns:
            List of clusters sorted by density (highest first)
        """
        clusters = []
        seen = set()
        
        for seed in self.G.nodes:
            if seed in seen:
                continue
            
            # Find w-core around this seed
            core = self._w_core(seed, w)
            
            if len(core) < 3:  # Minimum cluster size
                continue
            
            # Calculate cluster density
            sub = self.G.subgraph(core)
            n, e = sub.number_of_nodes(), sub.number_of_edges()
            density = 2 * e / (n * (n - 1)) if n > 1 else 0.0
            
            cid = str(uuid.uuid4())
            clusters.append({
                "id": cid,
                "seed": seed,
                "nodes": list(core),
                "density": round(density, 2)
            })
            
            seen.update(core)
        
        # Return top 10 by density
        return sorted(clusters, key=lambda c: c["density"], reverse=True)[:10]

    def _w_core(self, seed: str, w: int) -> set:
        """
        Find w-core around seed (edge weight ≥ w)
        
        A w-core is the set of nodes reachable from seed where all
        connecting edges have weight >= w.
        
        Args:
            seed: Starting node
            w: Minimum edge weight threshold
        
        Returns:
            Set of nodes in the w-core
        """
        core = {seed}
        queue = [seed]
        
        while queue:
            n = queue.pop(0)
            
            # Check neighbors
            for neigh in self.G[n]:
                if neigh not in core:
                    # Check if all edges n→neigh have weight >= w
                    edge_data = self.G[n][neigh]
                    if all(d.get("weight", 0) >= w for _, d in edge_data.items()):
                        core.add(neigh)
                        queue.append(neigh)
        
        return core


# ---------- Quick Demo ----------

if __name__ == "__main__":
    # Example usage
    skg = MicroSKG()
    
    text = """
    Pyramids need strong foundations. Foundations rely on solid ground.
    Ground shifts destroy pyramids. Strong foundations prevent destruction.
    """
    
    clusters = skg.bootstrap(text, user_id="u1", file_id="f1")
    
    print("Clusters found:")
    print(json.dumps(clusters, indent=2))
    
    print("\nPyVis export:")
    print(json.dumps(skg.to_pyvis_dict(), indent=2))
    
    print(f"\nGraph stats:")
    print(f"  Nodes: {skg.G.number_of_nodes()}")
    print(f"  Edges: {skg.G.number_of_edges()}")
