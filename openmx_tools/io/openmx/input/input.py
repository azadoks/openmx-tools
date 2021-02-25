# -*- coding: utf-8 -*-
"""Input utilities and constants for `openmx`."""

__all__ = ('write_input_file',)


_FORMAT_TYPE_MAPPING = {'number': '{:0.12f}', 'integer': '{:d}', 'string': '{}'}


def write_input_file(parameters, schema):
    """Write an OpenMX input file.

    :param parameters: Input parameters
    :param schema: Input parameters schema
    :returns: Input file content
    """
    input_file_content = ''
    for kw, value in parameters.items():
        value_type = schema['properties'][kw]['type']
        kw_str = kw.replace('_', '.')
        # 2D arrays and complex data
        if kw == 'ATOMS_SPECIESANDCOORDINATES':
            param_content = _write_atoms_spec_and_coords(value)
        elif kw == 'ATOMS_UNITVECTORS': 
            param_content = _write_array_block(value, item_type='number', tag='ATOMS.UNITVECTORS')
        elif kw == 'DEFINITION_OF_ATOMIC_SPECIES': 
            param_content = _write_def_atomic_species(value)
        elif kw == 'BAND_KPATH': 
            param_content = _write_band_kpath(value)
        elif kw == 'BAND_KPATH_UNITCELL': 
            param_content = _write_array_block(value, item_type='number', tag='BAND.KPATH.UNITCELL')
        # 1D arrays
        elif value_type == 'array':
            item_type = schema['properties'][kw]['items']['type']
            item_format = _FORMAT_TYPE_MAPPING[item_type]
            param_content = ' '.join([kw_str] + [item_format.format(item) for item in value]) + '\n'
        # Booleans must be -> ON/OFF for OpenMX
        elif value_type == 'boolean':
            param_content = ' '.join([kw_str, 'on' if value else 'off']) + '\n'
        # Scalar values
        else:
            value_format = _FORMAT_TYPE_MAPPING[value_type]
            param_content = ' '.join([kw_str, value_format.format(value)]) + '\n'
        input_file_content += param_content

    return input_file_content


def _write_def_atomic_species(def_atomic_species):
    """Write the `DEFINITION_OF_ATOMIC_SPECIES` input block."""
    ORB_MAP = {0: 's', 1: 'p', 2: 'd', 3: 'f'}
    TAG = 'DEFINITION.OF.ATOMIC.SPECIES'
    lines = []
    for specie, data in def_atomic_species.items():
        orbital_config = ''.join([
            f'{ORB_MAP[i]}{n_orb}' for i, n_orb in enumerate(data['pao']['orbital_configuration']) if n_orb != 0
        ])
        lines.append(f'\t{specie} {data["pao"]["file_stem"]}-{orbital_config} {data["pseudo"]}')
    block = _tag_block('\n'.join(lines), TAG)
    return block


def _write_atoms_spec_and_coords(atoms_spec_and_coords):
    """Write the `ATOMS.SPECIESANDCOORDINATES` input block."""
    TAG = 'ATOMS.SPECIESANDCOORDINATES'
    lines = []
    for i, data in enumerate(atoms_spec_and_coords):
        index = i + 1
        kind_name = data['specie']
        x, y, z = data['coords']
        up_charge = data['up_charge']
        down_charge = data['down_charge']
        lines.append(f'\t{index:d} {kind_name} {x:0.12f} {y:0.12f} {z:0.12f} {up_charge:0.6f} {down_charge:0.6f}')
    block = _tag_block('\n'.join(lines), TAG)
    return block


def _write_band_kpath():
    """Write the `BAND.KPATH` input block."""
    # TAG = 'BAND.KPATH'


def _write_array_block(array, item_type, tag):
    """Write an array input block.

    :param array: Array data to write
    :param type: JSON schema type of the items of the array
    :returns: OpenMX-formatted array input block
    """
    type_format = _FORMAT_TYPE_MAPPING[item_type]
    lines = []
    for row in array:
        lines.append('\t' + ' '.join([type_format.format(item) for item in row]))
    block = _tag_block('\n'.join(lines), tag)
    return block


def _tag_block(block, tag):
    """Add the open and close tags to an input block."""
    return f'<{tag}\n' + block + f'\n{tag}>\n'
