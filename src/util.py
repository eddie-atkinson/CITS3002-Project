"""Module containing utility functions.
"""
from Node import Node


def http_string(response_code: int, response_msg: str, messages: list) -> str:
    """Creates a HTTP response string with a given response code and messages.

    Args:
        response_code: HTTP response code to send
        response_msg: message to accompany HTTP code
        messages: list of strings to be included as content of the HTML
    """
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
    """Finds the UDP port for a neighbour from its name.

     Args:
        this_node: instance of the node class representing a given node in the network.
        node
        node_name: the name of the node whose port number is sought
    Returns:
        An integer representing the UDP port number of the neighbour
    Raises:
        KeyError: Couldn't find the neighbour's name in the neighbours dictionary
    """
    for port, name in this_node.neighbours.items():
        if name == node_name:
            return port
    raise KeyError(f"{this_node.name} couldn't find port number in neighbours for {node_name}")
