nextflow.enable.dsl=2

/*
* pipeline to find similarities between small-molecule binding sites 
* stored in PDB format in an input folder using SiteMine
* Note: you need a SiteMine license to run this pipeline
* For more information about SiteMine, please visit:
* https://www.uhh.de/naomi
*/

params.infolder_receptors = ""
params.infolder_pockets = ""
params.sitemine_exe_path = "/home/onur/software/SiteMine_1.2.0/SiteMine"
params.outfolder = "$projectDir/sitemine_workflow_results"
params.threads = 18
params.mode = "fast"

log.info """
    S I T E M I N E   W O R K F L O W
    =============================================
    infolder_receptors: ${params.infolder_receptors}
    infolder_pockets: ${params.infolder_pockets}
    sitemine_exe_path: ${params.sitemine_exe_path}
    outfolder: ${params.outfolder}
    threads: ${params.threads}
    mode: ${params.mode}
    """
    .stripIndent()

/*
* SiteMine has an unfortunate requirement that all receptor files
* must have a certain HEADER line that contains the PDB ID of the structure.
* We assume this will be missing from most user-provided files, so we add it here.
*/
process PREPARERECEPTORS {
    publishDir "${params.outfolder}/prepared_receptors", mode: 'copy'

    input:
    path receptor_file

    output:
    path "sitemine_*.pdb"

    script:
    """
    prepare_receptors.py \\
        --input ${receptor_file} \\
        --output sitemine_${receptor_file.getName()}
    """
}

process CONSTRUCTSITEMINEDB {
    publishDir params.outfolder, mode: 'copy'

    input:
    path 'prepared_receptors/*'

    output:
    path "receptors_db.sqlite"

    script:
    """
    ${params.sitemine_exe_path} --build --directory prepared_receptors -g "receptors_db.sqlite" \\
    --bindingSiteType DogSiteAlgorithm -t ${params.threads} --buildProgress --chunkSizeDBCreation 10
    """
}

process PREPAREEDFS {
    publishDir "${params.outfolder}/prepared_edfs", mode: 'copy'

    input:
    path pocket_file

    output:
    path "sitemine_*.edf"

    script:
    """
    prepare_edfs.py \\
        --input ${pocket_file} \\
        --output sitemine_${pocket_file.getName().replace('.pdb', '.edf')}
    """
}

process SITEMINE {
    publishDir params.outfolder, mode: 'copy'

    input:
    path 'prepared_receptors/*'
    path 'prepared_edfs/*'
    path sitemine_db

    output:
    path "sitemine_results"

    script:
    """
    sitemine.py \\
        --prepared_receptors_dir prepared_receptors \\
        --prepared_edfs_dir prepared_edfs \\
        --sitemine_db ${sitemine_db} \\
        --sitemine_exe ${params.sitemine_exe_path} \\
        --threads ${params.threads} \\
        --mode ${params.mode}
    """
}

workflow {
    receptor_files_ch = Channel.fromPath("${params.infolder_receptors}/*.pdb")
    prepare_receptors_ch = PREPARERECEPTORS(receptor_files_ch)
    
    // Collect all prepared receptors into a single directory
    prepared_receptors_collected = prepare_receptors_ch.collect()
    
    sitemine_db_ch = CONSTRUCTSITEMINEDB(prepared_receptors_collected)

    pocket_files_ch = Channel.fromPath("${params.infolder_pockets}/*.pdb")
    prepare_edfs_ch = PREPAREEDFS(pocket_files_ch)
    
    // Collect all prepared EDFs into a single directory
    prepared_edfs_collected = prepare_edfs_ch.collect()

    sitemine_ch = SITEMINE(prepared_receptors_collected, prepared_edfs_collected, sitemine_db_ch)

}