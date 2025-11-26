#!/usr/bin/env python

import argparse
import re
from pathlib import Path
from biopandas.pdb import PandasPdb

def extract_receptor_id(pocket_filename):
    """
    Extract the receptor ID from a pocket filename.
    E.g., 'AF-P21266-F1-model_v1_cavity_1.pdb' -> 'AF-P21266-F1-model_v4'
    Assumes the receptor uses v4 and the pocket uses v1.
    """
    # Remove _cavity_N.pdb suffix and replace v1 with v4
    receptor_id = re.sub(r'_v1_cavity_\d+\.pdb$', '_v4.pdb', pocket_filename)
    return receptor_id

def main():
    parser = argparse.ArgumentParser(description='Prepare EDF files for SiteMine from pocket PDB files')
    parser.add_argument('--input', required=True, help='Input pocket PDB file')
    parser.add_argument('--output', required=True, help='Output EDF file')
    args = parser.parse_args()

    # Read the pocket PDB file
    ppdb = PandasPdb().read_pdb(args.input)
    
    # Extract the receptor filename from the pocket filename
    pocket_filename = Path(args.input).name
    receptor_filename = extract_receptor_id(pocket_filename)
    
    # Create EDF content
    edf_lines = []
    
    # Add REFERENCE line pointing to the prepared receptor
    edf_lines.append(f'REFERENCE sitemine_{receptor_filename}')
    
    # Extract unique residues from the pocket PDB
    atom_df = ppdb.df['ATOM']
    
    # Group by chain, residue number, and residue name to get unique residues
    unique_residues = atom_df[['chain_id', 'residue_number', 'residue_name']].drop_duplicates()
    
    # Add RESIDUE lines for each residue in the pocket
    for _, row in unique_residues.iterrows():
        resname = row['residue_name']
        chain = row['chain_id']
        resnum = int(row['residue_number'])
        edf_lines.append(f'RESIDUE {resname} {chain} {resnum}')
    
    # Write the EDF file
    with open(args.output, 'w') as f:
        f.write('\n'.join(edf_lines))

if __name__ == '__main__':
    main()