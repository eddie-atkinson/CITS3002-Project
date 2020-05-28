from Node import Node


def http_string(response_code: int, response_msg: str, messages: list) -> str:
    response = (
        f"HTTP/1.0 {response_code} {response_msg}\n"
        + f"Content-Type: text/html\n"
        + f"Connection: Closed\n"
        + f"\n"
    )
    response += "<html><body>"
    for message in messages:
        response += f"<p>{message}</p>"
    response += "</body></html>"
    return response


def get_port_from_name(this_node: Node, node_name: str) -> int:
    for port, name in this_node.neighbours.items():
        if name == node_name:
            return port
    raise KeyError(f"Couldn't find port number in neighbours for {node_name}")
