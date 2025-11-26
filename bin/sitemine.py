#!/usr/bin/env python

import argparse
import subprocess
import os
from pathlib import Path
import glob

def main():
    parser = argparse.ArgumentParser(description='Run SiteMine to compare binding sites')
    parser.add_argument('--prepared_receptors_dir', required=True, help='Directory with prepared receptor PDB files')
    parser.add_argument('--prepared_edfs_dir', required=True, help='Directory with prepared EDF files')
    parser.add_argument('--sitemine_db', required=True, help='SiteMine database SQLite file')
    parser.add_argument('--sitemine_exe', required=True, help='Path to SiteMine executable')
    parser.add_argument('--threads', default='18', help='Number of threads to use')
    parser.add_argument('--mode', default='fast', help='SiteMine mode: fast or precise')
    args = parser.parse_args()

    # Create output directory
    output_dir = 'sitemine_results'
    os.makedirs(output_dir, exist_ok=True)

    # Get all EDF files
    edf_files = glob.glob(f'{args.prepared_edfs_dir}/*.edf')
    
    print(f"Found {len(edf_files)} EDF files to process")
    
    for edf_file in edf_files:
        edf_filename = Path(edf_file).stem
        
        # Extract receptor filename from EDF file
        # Read the first line of EDF to get the REFERENCE
        with open(edf_file, 'r') as f:
            first_line = f.readline().strip()
            if first_line.startswith('REFERENCE'):
                receptor_filename = first_line.split()[1]
                receptor_path = f'{args.prepared_receptors_dir}/{receptor_filename}'
                
                if not os.path.exists(receptor_path):
                    print(f"Warning: Receptor file not found: {receptor_path}")
                    continue
                
                # Create output subdirectory for this pocket
                pocket_output_dir = f'{output_dir}/{edf_filename}'
                
                # Build SiteMine command
                cmd = [
                    args.sitemine_exe,
                    '-g', args.sitemine_db,
                    '-f', receptor_path,
                    '-e', edf_file,
                    '-t', args.threads,
                    '-m', args.mode,
                    '-v', '4',
                    '--output', pocket_output_dir
                ]
                
                print(f"Processing: {edf_filename}")
                print(f"Command: {' '.join(cmd)}")
                
                # Run SiteMine
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    print(f"Error processing {edf_filename}:")
                    print(result.stderr)
                else:
                    print(f"Successfully processed {edf_filename}")

if __name__ == '__main__':
    main()
