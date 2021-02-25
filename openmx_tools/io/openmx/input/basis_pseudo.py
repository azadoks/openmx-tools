# -*- coding: utf-8 -*-
"""OpenMX `openmx` pseudoatomic orbital basis and pseudopotential tools."""

import os
import json

__all__ = ('get_rec_basis_pseudo', 'get_rec_basis_set_pseudos')


_DIR = os.path.dirname(os.path.abspath(__file__))


def get_rec_basis_pseudo(element, version='19', precision='standard', hardness='soft'):
    """Get pseudoatomic orbital basis and pseudopotential recommendation for an element."""
    table_file = '_'.join([version, precision, hardness]) + '.json'
    table_path = os.path.join(_DIR, 'data', 'basis_pseudo', table_file)
    if not os.path.exists(table_path):
        raise FileNotFoundError(f'A recommendations table does not exist for {version} {precision} {hardness}')
    
    with open(table_path, 'r') as stream:
        table = json.load(stream)

    return table[element]


def get_rec_basis_set_pseudos(structure, version='19', precision='standard', hardness='soft'):
    """Get pseudoatomic orbital basis and pseudopotential recommendations for a structure."""
    table_file = '_'.join([version, precision, hardness]) + '.json'
    table_path = os.path.join(_DIR, 'data', 'basis_pseudo', table_file)
    if not os.path.exists(table_path):
        raise FileNotFoundError(f'A recommendations table does not exist for {version} {precision} {hardness}')
    
    with open(table_path, 'r') as stream:
        table = json.load(stream)

    return {specie.symbol: table[specie.symbol] for specie in structure.species}
