#!/usr/bin/env python

import argparse
from pathlib import Path
from biopandas.pdb import PandasPdb

def main():
    parser = argparse.ArgumentParser(description='Prepare receptor PDB files for SiteMine')
    parser.add_argument('--input', required=True, help='Input PDB file')
    parser.add_argument('--output', required=True, help='Output PDB file with SiteMine header')
    args = parser.parse_args()

    # Read the PDB file
    ppdb = PandasPdb().read_pdb(args.input)
    
    # Extract a unique ID from the filename
    file_id = Path(args.input).stem
    
    # Add the SiteMine-required HEADER line
    # HEADER    HYDROLASE/HYDROLASE INHIBITOR           18-MAY-11   file_id (first 4 chars)
    header_id = file_id[:4].upper().ljust(4)
    ppdb.df['OTHERS'].loc[0, :] = [
        'HEADER',
        f'    HYDROLASE/HYDROLASE INHIBITOR           18-MAY-11   {header_id}',
        0
    ]
    
    # Write the output file
    ppdb.to_pdb(args.output)

if __name__ == '__main__':
    main()