<img src="docs/source/_static/ovo_diagram.png?raw=true" alt="OVO Overview" style="max-width:100%;">

# OVO, an open-source ecosystem for *de novo* protein design

[![PyPI version](https://img.shields.io/pypi/v/ovo)](https://pypi.org/project/ovo/) [![DOI](https://img.shields.io/badge/DOI-10.1101%2F2025.11.27.691041-blue)](https://doi.org/10.1101/2025.11.27.691041) [![Docs](https://img.shields.io/badge/docs-ovo.dichlab.org-green)](https://ovo.dichlab.org/docs/user_guide/installation.html) [![License](https://img.shields.io/pypi/l/ovo)](https://pypi.org/project/ovo/)

OVO (pronounced "oh-voh") consolidates models, workflows, data management, and interactive visualization into a scalable, 
high-performance, infrastructure-agnostic platform for *de novo* protein design. 
OVO features Nextflow-based workflow orchestration, a storage layer, and both command-line and web interfaces 
that democratize scaffold design, binder design and diversification, and validation workflows.

> Ovo, an Open-Source Ecosystem for De Novo Protein Design, 
> David Prihoda, Marco Ancona, Tereza Calounova, Adam Kral, Lukas Polak, 
> Hugo Hrban, Nicholas J. Dickens, Danny Asher Bitton 
> bioRxiv 2025.11.27.691041; doi: https://doi.org/10.1101/2025.11.27.691041

## 🐣 Getting started

To get started with OVO, please refer to the **[User Guide](https://ovo.dichlab.org/docs/user_guide/installation.html)**.

To preview the OVO web app (without the ability to submit jobs), see the [OVO Demo Server](https://ovo.dichlab.org/demo).

## ▶️ Demo video

https://github.com/user-attachments/assets/7b339fa6-c6de-467d-90d0-5cd15f83c498

## 🧬 Methods & Acknowledgments

We gratefully acknowledge the authors and developers of the following methods and tools available from OVO:

| Method Name              | Description                                        | Reference / Paper                                                                                                                   | Link                                                                                                   |
|--------------------------|----------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| RFdiffusion              | Diffusion-based protein structure generation       | [Watson et al. 2023](https://doi.org/10.1038/s41586-023-06415-8)                                                                    | [GitHub](https://github.com/RosettaCommons/RFdiffusion)                                                |
| RFdiffusion3             | Design of all-atom biomolecular interactions       | [Butcher et al. 2025](https://doi.org/10.1101/2025.09.18.676967)                                                                    | [GitHub](https://github.com/RosettaCommons/foundry/blob/production/models/rfd3/README.md)              |
| ProteinMPNN              | Protein sequence design for fixed backbones        | [Dauparas et al. 2022](https://doi.org/10.1126/science.add2187)                                                                     | [GitHub](https://github.com/dauparas/ProteinMPNN)                                                      |
| LigandMPNN               | Atomic context-conditioned protein sequence design | [Dauparas et al. 2025](https://doi.org/10.1038/s41592-025-02626-1)                                                                  | [GitHub](https://github.com/dauparas/LigandMPNN)                                                      |
| PyRosetta FastRelax      | Binder sequence design protocol                    | [Bennett et al. 2023](https://doi.org/10.1038/s41467-023-38328-5)                                                                   | [GitHub](https://github.com/nrbennet/dl_binder_design)                                                      |
| AlphaFold2 / ColabDesign | Deep learning-based protein structure prediction   | [Jumper et al. 2021](https://doi.org/10.1038/s41586-021-03819-2)                                                                    | [GitHub (AlphaFold2)](https://github.com/google-deepmind/alphafold), [GitHub (ColabDesign)](https://github.com/sokrypton/ColabDesign) |
| BindCraft                | Binder design using AF2 backpropagation            | [Pacesa et al. 2024](https://doi.org/10.1101/2024.09.30.615802)                                                                     | [GitHub](https://github.com/martinpacesa/BindCraft)                                                    |
| Boltz                    | Deep learning-based protein structure prediction   | [Wohlwend et al. 2024](https://doi.org/10.1101/2024.11.19.624167), [Passaro et al. 2025](https://doi.org/10.1101/2025.06.14.659707) | [GitHub](https://github.com/jwohlwend/boltz)                                                           |
| ESM-1v                   | Protein language model for variant effect          | [Meier et al. 2021](https://doi.org/10.1101/2021.07.09.450648)                                                                      | [GitHub](https://github.com/facebookresearch/esm)                                                      |
| ESM-IF                   | Inverse folding with protein language models       | [Hsu et al. 2022](https://doi.org/10.1101/2022.04.10.487779)                                                                        | [GitHub](https://github.com/facebookresearch/esm)                                                      |
| DSSP                     | Secondary structure assignment                     | [Kabsch & Sander 1983](https://doi.org/10.1002/bip.360221211), [Joosten et al. 2010](https://doi.org/10.1093/nar/gkq1105)           | [GitHub](https://github.com/PDB-REDO/dssp)                                                             |
| PEP-Patch                | Protein surface patches analysis                   | [Kufareva et al. 2023](https://doi.org/10.1021/acs.jcim.3c01490)                                                                    | [GitHub](https://github.com/liedllab/surface_analyses)                                                 |
| Protein-Sol              | Protein solubility prediction                      | [Hebditch et al. 2017](https://doi.org/10.1093/bioinformatics/btx345)                                                               | [Web](https://protein-sol.manchester.ac.uk/)

## 🛠️ Development

OVO is an open-source project and we welcome contributions from the community.

Please refer to the [Developer Guide](https://ovo.dichlab.org/docs/developer_guide/) for information on how to contribute to OVO.
