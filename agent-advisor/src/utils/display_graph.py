from pathlib import Path

from src.workflow_agentic.graph import get_compiled_graph


def generate_graph_image(output_path: str = "../graph.png") -> str:
    graph = get_compiled_graph()
    png_data = graph.get_graph().draw_mermaid_png()

    path = Path(output_path)
    path.write_bytes(png_data)
    print(f"Grafo salvo em: {path.resolve()}")
    return str(path.resolve())


if __name__ == "__main__":
    generate_graph_image()
