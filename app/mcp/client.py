from dataclasses import dataclass
from typing import Optional


@dataclass
class MCPClient:
    agent_id: str
    server_url: Optional[str] = None

    def connect(self, url: str) -> None:
        self.server_url = url


def connect_mcp(agent_id: str, url: str) -> MCPClient:
    client = MCPClient(agent_id=agent_id)
    client.connect(url)
    return client
