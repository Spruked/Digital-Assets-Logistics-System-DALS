# goat_skill_graph.py
import networkx as nx
from .goat_models import SkillNode
from typing import List, Dict

class GOATSkillGraph:
    def __init__(self):
        self.G = nx.DiGraph()

    def add_skill(self, node: SkillNode):
        self.G.add_node(node.id, **node.dict())
        for prereq in node.prereqs:
            self.G.add_edge(prereq, node.id, relation="requires")

    def get_learning_path(self, start: str, goal: str) -> List[str]:
        try:
            return list(nx.shortest_path(self.G, start, goal))
        except nx.NetworkXNoPath:
            return self._find_alternative_path(start, goal)

    def _find_alternative_path(self, start: str, goal: str) -> List[str]:
        # Fallback: BFS from start to any node with "goal" in name
        for node in nx.bfs_tree(self.G, start):
            if goal.lower() in self.G.nodes[node].get("name", "").lower():
                return list(nx.shortest_path(self.G, start, node))
        return []