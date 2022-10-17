"""This module contains functions for converting a script to a :py:mod:`.networkx`
"""
import typing as tp
from copy import copy

import networkx as nx  # type: ignore

from df_script_parser.utils.code_wrappers import StringTag, Python, String
from df_script_parser.utils.namespaces import Call
from df_script_parser.utils.validators import keywords_dict
from df_script_parser.utils.exceptions import ScriptValidationError


def get_destination(label: StringTag, kwargs: tp.Optional[dict] = None):
    if isinstance(label, Python):
        resolved_value = label.metadata.get("resolved_value")
        if resolved_value is None:
            raise RuntimeError(f"Resolved value is none: {label.__dict__}")
        if isinstance(resolved_value, Python):
            parsed_value = resolved_value.metadata.get("parsed_value")
            if parsed_value is None:
                raise RuntimeError(f"Parsed value is none: {label.__dict__}")
            if isinstance(parsed_value, tuple):
                if isinstance(parsed_value[0], String) and isinstance(parsed_value[1], String):
                    return parsed_value[0].display_value, parsed_value[1].display_value
    call_name = label.absolute_value.rpartition("(")[0].split(".")[-1]
    if not call_name in ["forward", "repeat", "backward", "to_start", "to_fallback"]:
        return ("NONE",)
    else:
        if call_name == "to_fallback":
            return kwargs["fallback_label"]
        elif call_name == "to_start":
            return kwargs["start_label"]
        elif call_name == "repeat":
            return kwargs["current_label"]
        elif call_name == "backward":
            return get_by_index_shifting(**kwargs, increment_flag=False)
        elif call_name == "forward":
            return get_by_index_shifting(**kwargs, increment_flag=True)


def script2graph(
    traversed_path: tp.List[StringTag],
    final_value: tp.Union[StringTag, Call],
    paths: tp.List[tp.List[str]],
    graph: nx.MultiDiGraph,
    script: dict,
    start_label: tuple,
    fallback_label: tuple,
):
    if len(traversed_path) == 0:
        raise ScriptValidationError(f"traversed_path is empty: {traversed_path, final_value, paths}")

    if traversed_path[0] in keywords_dict["GLOBAL"]:
        node_name: tp.Union[tp.Tuple[str], tp.Tuple[str, str]] = ("GLOBAL",)
    else:
        node_name = (traversed_path[0].absolute_value, traversed_path[1].absolute_value)

    graph.add_node(node_name, ref=copy(paths[len(node_name)]), local=traversed_path[1] in keywords_dict["LOCAL"])

    if traversed_path[len(node_name)] in keywords_dict["TRANSITIONS"]:
        if not isinstance(final_value, StringTag):
            raise ScriptValidationError(
                f"Condition is not a ``StringTag: {final_value}. traversed_path={traversed_path}"
            )
        destination_kwargs = {
            "start_label": start_label,
            "fallback_label": fallback_label,
            "current_label": node_name,
            "script": script,
        }
        destination = get_destination(traversed_path[len(node_name) + 1], kwargs=destination_kwargs)
        graph.add_edge(
            node_name,
            destination,
            label_ref=copy(paths[len(node_name) + 1]),
            label=traversed_path[len(node_name) + 1].display_value,
            condition_ref=copy(paths[len(node_name) + 2]),
            condition=final_value.display_value,
        )


def get_by_index_shifting(
    script: dict,
    current_label: tuple,
    fallback_label: tuple,
    increment_flag: bool = True,
    cyclicality_flag: bool = True,
    **kwargs,
) -> tuple:
    if current_label == ("GLOBAL",):
        return fallback_label
    flow_label, node_label = current_label
    labels = list(script.get(flow_label, {}))

    if node_label not in labels:
        return fallback_label

    label_index = labels.index(node_label)
    label_index = label_index + 1 if increment_flag else label_index - 1
    if not (cyclicality_flag or (0 <= label_index < len(labels))):
        return fallback_label
    label_index %= len(labels)

    return flow_label, labels[label_index]
