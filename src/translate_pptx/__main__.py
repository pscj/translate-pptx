#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Entry point for running translate_pptx as a module.
Usage: python -m translate_pptx <input.pptx> <target_language> [model]
"""

from ._terminal import command_line_interface

if __name__ == '__main__':
    command_line_interface()
