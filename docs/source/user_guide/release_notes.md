# Release Notes

### 1.1.0 (latest)

*Release date: April 22, 2026*

#### New features

- **Boltz-2 integration** for structure refolding with RMSD computation and standardized descriptor keys (<a href="https://github.com/MSDLLCpapers/ovo/commit/00179b96f586e011164595d7f601831bf9e912c5" target="_blank">00179b9</a>)
- **Clustering tab** on Designs page with interactive cluster selection and visualization using Foldseek structural clustering with UMAP visualization (<a href="https://github.com/MSDLLCpapers/ovo/commit/8a206de99f843699c571e9ce82b3610761624db4" target="_blank">8a206de</a>, <a href="https://github.com/MSDLLCpapers/ovo/commit/39ddedbb9e570e2acfe09c0909cc9dde186549bd" target="_blank">39ddedb</a>)
  - Example clustering result: <a href="https://ovo.dichlab.org/demo/designs?project_id=b8e657bb-b0b0-423e-9235-383a6d8f74e5&rounds=79935f30-2088-4dfe-996d-5433aeeb37fc&design_view=%F0%9F%AB%A7+Clustering&pool_ids=bbc%2Cqki%2Cmmo%2Cavz" target="_blank">RFdiffusion miniprotein binders</a> and <a href="https://ovo.dichlab.org/demo/designs?project_id=b8e657bb-b0b0-423e-9235-383a6d8f74e5&rounds=4d42a890-eb87-4edc-a624-fbec5e62969e&design_view=%F0%9F%AB%A7+Clustering&selected_design=ovo_ogc_04_011_seq03" target="_blank">RFdiffusion oxidoreductase motif scaffolding</a> from OVO publication
- **Regression analysis tab** that enables uploading experimental data or other numeric endpoints and correlating them with computed descriptors (<a href="https://github.com/MSDLLCpapers/ovo/commit/8e5ba8f4cec3ce00a5721fb61e0dc6fa859ca51c" target="_blank">8e5ba8f</a>)
  - Example regression analysis: <a href="https://ovo.dichlab.org/demo/designs?attachment_5a70f535-59c7-4fb3-ae77-e35de1a3ae0a=true&design_view=%F0%9F%93%89+Regression&pool_ids=mau&project_id=0d8b10e1-0631-4911-b56f-63885f530c79&rounds=99b865a3-8ee9-44a7-8bb6-771237d65085&regression_tab=Clustermap" target="_blank">Proteinbase Nipah Binder</a> correlating descriptors with experimental binding data</a>
- **Processing rejected BindCraft trajectories** into the database for inspection (<a href="https://github.com/MSDLLCpapers/ovo/commit/c9e8d319e022a6a97327f20a47b6b1953ebdf656" target="_blank">c9e8d31</a>)
- **Advanced job monitoring** on Job Detail page with real-time task status, log output, execution timeline, and workflow schema and report visualization (<a href="https://github.com/MSDLLCpapers/ovo/commit/48b54c6de64241ac9a70630320f7d06b4fda5c68" target="_blank">48b54c6</a>)
- **Resuming failed workflows** on Job Detail page using Nextflow resume functionality
- **Workflow summary visualization** on Job Detail page showing design statistics and acceptance rates (<a href="https://github.com/MSDLLCpapers/ovo/commit/78374e932744438568d13dd765dd2b6703cd2f05" target="_blank">78374e9</a>)
- **Storage in ZIP archives** with multi-threaded write support to reduce overhead of managing many PDB files. To enable this, set `archive_method: zip` under `storage` section in ovo config (<a href="https://github.com/MSDLLCpapers/ovo/commit/c169bc322fcbf5566c2afac88fe4e846edf6f881" target="_blank">c169bc3</a>)
- **Refactored plugin definitions** enabling custom web app extension points using `get_extension_points` function - more info coming soon! (<a href="https://github.com/MSDLLCpapers/ovo/commit/6903ecc4359685b0d995c2325eea0d3dbcbb2294" target="_blank">6903ecc</a>)
- **Redesigned sidebar with Workflows page** with workflow cards and search. Use the Pin feature to see workflows in the sidebar. (<a href="https://github.com/MSDLLCpapers/ovo/commit/6903ecc4359685b0d995c2325eea0d3dbcbb2294" target="_blank">6903ecc</a>)
- **Project page and attachments** - New dedicated page showing project description, settings, storage path (for admins), project statistics, and enables uploading file attachments (<a href="https://github.com/MSDLLCpapers/ovo/commit/6903ecc4359685b0d995c2325eea0d3dbcbb2294" target="_blank">6903ecc</a>, <a href="https://github.com/MSDLLCpapers/ovo/commit/025f54d006916782637f8291465aef77360269c6" target="_blank">025f54d</a>)
- **Project list** dialog window that shows recent projects with search capability
- **Design labeling** - designs can now be labeled with custom tags or simplified labels (❤️ or 👎) for easier tracking and filtering (<a href="https://github.com/MSDLLCpapers/ovo/commit/a2308e8304fcd4c4bb268f0c4b018a3eb30ee8ea" target="_blank">a2308e8</a>)

#### Usability improvements

- **Sequence-only design support** - designs can now be uploaded from a CSV file and analyzed with ProteinQC (<a href="https://github.com/MSDLLCpapers/ovo/commit/1a14f955c8de3741ed993eebd783aa78ee325b84" target="_blank">1a14f95</a>)
- **Optimized PDB sequence extraction** using native Python parser instead of BioPython, eliminating CPU bottleneck in workflow result processing (<a href="https://github.com/MSDLLCpapers/ovo/commit/e8f2be6d668e154a07292e48f9599b84a69fdd59" target="_blank">e8f2be6</a>)
- **Custom backbone input support** enable further sequence design of specific backbones in RFdiffusion end-to-end pipeline. CLI or Python API only - use `rfdiffusion_params.custom_backbones`. Support in web app coming soon (<a href="https://github.com/MSDLLCpapers/ovo/commit/78374e932744438568d13dd765dd2b6703cd2f05" target="_blank">78374e9</a>)
- **Support importing outdated projects** by applying migrations during import (<a href="https://github.com/MSDLLCpapers/ovo/commit/09eeff67f3a42e0d28b4ad7897dc7757bf25510d" target="_blank">09eeff6</a>)
- **Automatic CIF->PDB conversion** in RFdiffusion structure input (<a href="https://github.com/MSDLLCpapers/ovo/commit/3d7c04f9727154de25ffefd4ece237cfb566f573" target="_blank">3d7c04f</a>)
- **Descriptor query speed improvements** using new DB index on descriptor_key (<a href="https://github.com/MSDLLCpapers/ovo/commit/de1ad165b405efcc8fdaaea7b4698b30cca6f1a1" target="_blank">de1ad16</a>)
- **Jupyter notebook usability** improvements: better database connection handling and more design logic functions (<a href="https://github.com/MSDLLCpapers/ovo/commit/e75cfbc650a1cd3028a9342f764cf743b2226987" target="_blank">e75cfbc</a>)
- **Contig parsing** refactored into two functions (`parse_contig_for_input_structure` and `parse_contig_for_output_structure`)
- **Better support for multiple designed chains** in scaffold design by improved contig parsing (<a href="https://github.com/MSDLLCpapers/ovo/commit/78374e932744438568d13dd765dd2b6703cd2f05" target="_blank">78374e9</a>)
- **AF2 output target structure renumbering** and tracking AF2 target interface residues as descriptors (<a href="https://github.com/MSDLLCpapers/ovo/commit/78374e932744438568d13dd765dd2b6703cd2f05" target="_blank">78374e9</a>)
- **Jupyter Singularity/Apptainer socket support** in `ovo scheduler jupyter` - Enables proper Jupyter notebook integration when using containerization (<a href="https://github.com/MSDLLCpapers/ovo/commit/48b54c6de64241ac9a70630320f7d06b4fda5c68" target="_blank">48b54c6</a>)
- **Processing descriptor workflow file outputs** OVO plugins can now easily process per-design file outputs such as PDBs produced by design or descriptor workflows by calling `read_per_design_files` (<a href="https://github.com/MSDLLCpapers/ovo/commit/db131b40b953b34c44814284dbc758148f79c6fa" target="_blank">db131b4</a>)
- **Automatic chain selection** when submitting descriptor workflows and easier preparation of descriptor workflow input files using `prepare_design_structures` and `prepare_design_sequences` (<a href="https://github.com/MSDLLCpapers/ovo/commit/1a14f955c8de3741ed993eebd783aa78ee325b84" target="_blank">1a14f95</a>)

#### Bug fixes

- **Job duration display** fixed showing excessive/increasing durations for completed jobs (Nextflow log parsing)
- **Pandas 3.0 compatibility** fixed in dependency constraints (<a href="https://github.com/MSDLLCpapers/ovo/commit/2000d7b55a18770edd5684cc4949cb1e2b630117" target="_blank">2000d7b</a>)
- **PostgreSQL compatibility** fixed: func.now() for timestamp queries (<a href="https://github.com/MSDLLCpapers/ovo/commit/d628ade79ecbbea6d50eb26f4a2914a098497881" target="_blank">d628ade</a>, <a href="https://github.com/MSDLLCpapers/ovo/commit/6cc4359c94b0c4502a6a9f230885981f007fe6aa" target="_blank">6cc4359</a>)
- **AWS HealthOmics compatibility** fixed with container detection and Nextflow process syntax (<a href="https://github.com/MSDLLCpapers/ovo/commit/196a493725c24a27995556716a6dc0661401da41" target="_blank">196a493</a>)
- **Streamlit 1.54 round selection** widget behavior fixed (<a href="https://github.com/MSDLLCpapers/ovo/commit/170acd7e3079592b98fa84c0a1a740888729f78d" target="_blank">170acd7</a>)
- **Empty BindCraft results** processing fixed (<a href="https://github.com/MSDLLCpapers/ovo/commit/b524822945ede88ca8d85c4a9198ed20a1ce349c" target="_blank">b524822</a>)
- **Missing ESMFold PAE values** fixed in ESMFold pipeline (<a href="https://github.com/MSDLLCpapers/ovo/commit/bd2d61b8504c98c2eaac70ceeddb5df1536ec0c4" target="_blank">bd2d61b</a>)
- **Exporting UnknownWorkflow types** fixed
- **Random seed side effects** causing similar pool IDs was fixed by avoiding global random.seed() call in color picker (<a href="https://github.com/MSDLLCpapers/ovo/commit/9cc72d91ed5cd2cd50e952e28c984023b43b0b1b" target="_blank">9cc72d9</a>)

---

### 1.0.2

*Release date: February 10, 2026*

#### New features

- **`ovo init plugin` command** - New CLI command that generates a new OVO plugin folder with examples for custom descriptors, design views, Nextflow pipelines and conda environments (<a href="https://ovo.dichlab.org/docs/developer_guide/plugin_development.html" target="_blank">documentation</a>, <a href="https://github.com/MSDLLCpapers/ovo/commit/d2a1043c47640a728048f7da54e2d997e2f15887" target="_blank">d2a1043</a>)
- **Setting BindCraft advanced settings from UI** - Added UI controls for configuring acceptance thresholds directly in BindCraft submission form (<a href="https://github.com/MSDLLCpapers/ovo/commit/22e4c05b52f42327294ec599d42496cf2022fc77" target="_blank">22e4c05</a>)

#### Bug fixes

- **Singularity/Apptainer mount paths** - Removed read-only (`:ro`) flag from shared mount paths to allow writing to mounted directories (<a href="https://github.com/MSDLLCpapers/ovo/commit/ff993373a98e6b75175c359d6398107a745e9286" target="_blank">ff99337</a>)
