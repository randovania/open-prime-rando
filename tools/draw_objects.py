import argparse
import collections
import os
import typing
from pathlib import Path

import graphviz
import networkx
from retro_data_structures.asset_manager import IsoFileProvider
from retro_data_structures.formats.script_object import ScriptInstance
from retro_data_structures.game_check import Game

from open_prime_rando.echoes.asset_ids import world
from open_prime_rando.patcher_editor import PatcherEditor


def _draw_component(dot: graphviz.Digraph, instances: list[ScriptInstance],
                    namer: typing.Callable[[ScriptInstance], str]):
    for instance in instances:
        dot.node(name=str(instance.id), label=namer(instance))

    for instance in instances:
        for con in instance.connections:
            dot.edge(str(instance.id), str(con.target), label=f"{con.state.name} - {con.message.name}")

    dot.render(cleanup=True, format="png")

def draw_objects(editor: PatcherEditor, world_name: str, area_name: str):
    mlvl = editor.get_mlvl(world.NAME_TO_ID_MLVL[world_name])
    area = mlvl.get_area(world.load_dedicated_file(world_name).NAME_TO_ID_MREA[area_name])

    graph = networkx.DiGraph()

    name_count: dict[str, int] = collections.defaultdict(int)

    for instance in area.all_instances:
        name_count[instance.name] += 1
        graph.add_node(instance.id)
        for con in instance.connections:
            graph.add_node(con.target)
            graph.add_edge(instance.id, con.target)

    def namer(inst: ScriptInstance):
        name = inst.name
        if name:
            if name_count[name] > 1:
                name += f" ({inst.id})"
        else:
            name = str(inst.id)
        return name

    group_i = 1
    for comp in networkx.weakly_connected_components(graph):
        if len(comp) < 2:
            continue

        _draw_component(
            graphviz.Digraph(name=f"{area_name} ({group_i})"),
            [instance for instance in area.all_instances if instance.id in comp],
            namer,
        )

        group_i += 1


def main():
    iso = os.getenv("PRIME2_ISO")

    parser = argparse.ArgumentParser()
    parser.add_argument("--game", required=False, default="echoes", choices=["echoes"])
    parser.add_argument("--iso", required=iso is None, type=Path, default=iso,
                        help="Path to where the ISO.")
    parser.add_argument("world", help="Name of the world to check, as used in the schema")
    parser.add_argument("area", help="Name of the area to check, as used in the schema")
    args = parser.parse_args()

    draw_objects(
        PatcherEditor(IsoFileProvider(args.iso), Game.ECHOES),
        args.world, args.area,
    )


if __name__ == '__main__':
    main()
