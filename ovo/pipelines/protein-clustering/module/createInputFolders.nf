nextflow.enable.dsl = 2

process createInputFolders {
    executor 'local'
    input:
        path inputs
        val dir_name
    output:
        path "${dir_name}", emit: pdb_dir
    script:
    """
        echo "Creating input folder: ${dir_name}"
        mkdir -p ${dir_name}
        cp ${inputs} ${dir_name}
        echo "Input folder created: ${dir_name}"
    """
}
