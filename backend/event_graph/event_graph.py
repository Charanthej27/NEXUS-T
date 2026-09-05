import networkx as nx


class EventGraph:
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_event(self, event_id: str, event_type: str, data: dict):
        self.graph.add_node(
            event_id,
            event_type=event_type,
            data=data,
        )

    def connect(self, source: str, target: str, relationship: str):
        self.graph.add_edge(
            source,
            target,
            relationship=relationship,
        )

    def get_related_events(self, event_id: str):
        if event_id not in self.graph:
            return []

        related = []

        for node in self.graph.successors(event_id):
            related.append({
                "event_id": node,
                **self.graph.nodes[node],
                "relationship": self.graph.edges[event_id, node]["relationship"],
            })

        return related

    def get_event_chain(self, event_id: str):
        if event_id not in self.graph:
            return []

        chain = []

        for node in nx.descendants(self.graph, event_id):
            chain.append({
                "event_id": node,
                **self.graph.nodes[node],
            })

        return chain

    def summary(self):
        return {
            "events": self.graph.number_of_nodes(),
            "relationships": self.graph.number_of_edges(),
        }