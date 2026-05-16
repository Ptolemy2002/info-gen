from pytypes import rgb_bound_argtype
from argparse import ArgumentParser

def add_args_color(parser: ArgumentParser) -> ArgumentParser:
    parser.add_argument('--min-r', '-mnr', type=rgb_bound_argtype, default=0, help="Minimum red value for color generation (0-255, default: 0)")
    parser.add_argument('--max-r', '-mxr', type=rgb_bound_argtype, default=255, help="Maximum red value for color generation (0-255, default: 255)")
    parser.add_argument('--exact-r', '-r', type=rgb_bound_argtype, default=None, help="Exact red value for color generation (0-255). If specified, overrides min and max red values.")
    parser.add_argument('--min-g', '-mng', type=rgb_bound_argtype, default=0, help="Minimum green value for color generation (0-255, default: 0)")
    parser.add_argument('--max-g', '-mxg', type=rgb_bound_argtype, default=255, help="Maximum green value for color generation (0-255, default: 255)")
    parser.add_argument('--exact-g', '-g', type=rgb_bound_argtype, default=None, help="Exact green value for color generation (0-255). If specified, overrides min and max green values.")
    parser.add_argument('--min-b', '-mnb', type=rgb_bound_argtype, default=0, help="Minimum blue value for color generation (0-255, default: 0)")
    parser.add_argument('--max-b', '-mxb', type=rgb_bound_argtype, default=255, help="Maximum blue value for color generation (0-255, default: 255)")
    parser.add_argument('--exact-b', '-b', type=rgb_bound_argtype, default=None, help="Exact blue value for color generation (0-255). If specified, overrides min and max blue values.")
    return parser