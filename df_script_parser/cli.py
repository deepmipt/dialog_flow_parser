"""This module contains cli wrappers around parser tools
"""
from pathlib import Path
import argparse
from df_script_parser.tools import py2yaml, yaml2py, py2graph, graph2py


def is_dir(arg: str) -> Path:
    """Check that the passed argument is a directory

    :param arg: Argument to check
    :type arg: str
    :return: :py:class:`.Path` instance created from arg if it is a directory
    """
    path = Path(arg)
    if path.is_dir():
        return path
    raise argparse.ArgumentTypeError(f"Not a directory: {path}")


def is_file(arg: str) -> Path:
    """Check that the passed argument is a file

    :param arg: Argument to check
    :type arg: str
    :return: :py:class:`.Path` instance created from arg if it is a file
    """
    path = Path(arg)
    if path.is_file():
        return path
    raise argparse.ArgumentTypeError(f"Not a file: {path}")


py2file_parser = argparse.ArgumentParser()
py2file_parser.add_argument(
    "-rf",
    "--root_file",
    required=True,
    metavar="ROOT_FILE",
    help="Python file to start parsing with",
    type=is_file,
)
py2file_parser.add_argument(
    "-d",
    "--project_root_dir",
    required=True,
    metavar="PROJECT_ROOT_DIR",
    help="Directory that contains all the local files required to run ROOT_FILE",
    type=is_dir,
)
py2file_parser.add_argument(
    "-o",
    "--output_file",
    required=True,
    metavar="OUTPUT_FILE",
    help="File to store parser output in",
    type=str,
)
py2file_parser.add_argument(
    "-r",
    "--requirements",
    metavar="REQUIREMENTS",
    help="File with project requirements to override those collected by parser",
    type=is_file,
    required=False,
    default=None,
)

file2py_parser = argparse.ArgumentParser()
file2py_parser.add_argument(
    "-i",
    "--input_file",
    required=True,
    metavar="INPUT_FILE",
    help="File to load",
    type=is_file,
)
file2py_parser.add_argument(
    "-od",
    "--output_dir",
    required=True,
    metavar="OUTPUT_DIR",
    help="Path to the directory to extract project to",
    type=is_dir,
)


def py2yaml_cli():
    """:py:func:`.py2yaml` cli wrapper"""
    parser = argparse.ArgumentParser(parents=[py2file_parser], description=py2yaml.__doc__.split("\n\n", maxsplit=1)[0])
    args = parser.parse_args()
    py2yaml(**vars(args))


def py2graph_cli():
    """:py:func:`.py2graph` cli wrapper"""
    parser = argparse.ArgumentParser(parents=[py2file_parser], description=py2graph.__doc__.split("\n\n", maxsplit=1)[0])
    args = parser.parse_args()
    py2graph(**vars(args))


def yaml2py_cli():
    """:py:func:`.yaml2py` cli wrapper"""
    parser = argparse.ArgumentParser(parents=[file2py_parser], description=yaml2py.__doc__.split("\n\n", maxsplit=1)[0])
    args = parser.parse_args()
    yaml2py(**vars(args))


def graph2py_cli():
    """:py:func:`.graph2py` cli wrapper"""
    parser = argparse.ArgumentParser(parents=[file2py_parser], description=graph2py.__doc__.split("\n\n", maxsplit=1)[0])
    args = parser.parse_args()
    graph2py(**vars(args))
