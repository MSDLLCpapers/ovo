# OVO Plugin Development

Please use [the Discussions tab](https://github.com/MSDLLCpapers/ovo/discussions) on GitHub
for questions and support regarding plugin development.

Example plugins:

- [OVO promb](https://github.com/MSDLLCpapers/ovo-promb)
- [OVO ProteinDJ](https://github.com/MSDLLCpapers/ovo-proteindj)

---

## Tutorials

### Developing descriptor plugins for OVO

<iframe width="560" height="315" src="https://www.youtube.com/embed/wFZ_v8vm_70?si=_W240wYoLUdLLTcd" 
title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

#### Part 1: Developing a simple UI plugin for OVO

This section describes how to develop a simple UI plugin for OVO that displays 
a custom tab on the "🐣 Designs" page in the OVO web app.
The limitation of UI plugins is that they cannot introduce additional dependencies, 
and they have to run "on the fly" in the OVO web app, 
which means that they cannot run any heavy computations or use any large models.

Starting at 13:48 in the **video tutorial above**.

<details>
<summary>Show step-by-step instructions</summary>
Start by installing latest version of OVO (pip recommended):

```bash
pip install --upgrade ovo
```

Create your plugin directory using `ovo init plugin`:

```bash
ovo init plugin
# enter a name for your new plugin directory, 
# select "ui" plugin template, 
# and follow the instructions
```

Install your plugin in editable mode:

```bash
pip install -e ./ovo_your_plugin_directory
```

Now you can start developing your plugin by editing the `design_view_....py` file in your plugin directory.

This page will be accessible as a tab on the "🐣 Designs" page in the OVO web app.

Please refer to the **video tutorial above** starting at 13:48 for a step-by-step walkthrough.

See the built-in [OVO design pages](https://github.com/MSDLLCpapers/ovo/tree/develop/ovo/app/pages/designs) for inspiration.

Please refer to [Streamlit documentation](https://docs.streamlit.io/) for more information on how to develop Streamlit apps.

</details>

&nbsp;

#### Part 2: Developing a protein analysis "descriptor" plugin for OVO

This section describes how to develop a protein analysis "descriptor" plugin for OVO, 
which adds a new tab to the OVO "🐣 Designs" page that allows users to analyze their designs using a custom method.

Starting at 25:09 in the **video tutorial above**.

<details>
<summary>Show step-by-step instructions</summary>
Start by installing latest version of OVO (pip recommended):

```bash
pip install --upgrade ovo
```

Create your plugin directory using `ovo init plugin`:

```bash
ovo init plugin
# enter a name for your new plugin directory, 
# select "descriptor" plugin template, 
# and follow the instructions
```

Install your plugin in editable mode:

```bash
pip install -e ./ovo_your_plugin_directory
```

This will add a new tab on the "🐣 Designs" page in the OVO web app where you can submit your workflow and visualize the results.

The next steps will depend on the specific analysis method you want to implement, but in general you will need to:

- Edit the `envs/yourtool.yml` file to add any dependencies needed for your analysis method
  - Contribute a Dockerfile to the [ovo-containers repository](https://github.com/MSDLLCpapers/ovo-containers) so that we can prepare a pre-built container and make it available for all users to download
- Edit the shell script in the Nextflow `pipelines/.../main.nf` file to call your analysis method.
- Test the workflow using the shell script found in `pipelines/.../local/nextflow_test.sh`. The workflow should produce a CSV file with descriptor values. 
- For each column in the CSV file that should be saved in the database, create a Descriptor object in the `descriptors_yourplugin.py` file so that they can be stored in the database and visualized in the UI
- Now you can submit from the OVO web app and visualize the results
  - If the workflow fails on missing Design IDs, edit the `design_id_mapping` in the `process_results` function in `models_yourplugin.py` to make sure that the ID column in the CSV file from the workflow results is correctly mapped to the Design IDs in the OVO database

To add additional parameters to the workflow:

- Add the parameters to the `pipelines/.../nextflow.config` file and the `pipelines/.../nextflow_schema.json` file
- Edit the `pipelines/.../main.nf` file to accept the new parameters and use them in your analysis method
- Add the new parameters to the test script `pipelines/.../local/nextflow_test.sh` and make sure the test workflow runs successfully
- Edit the `models_yourplugin.py` file to add the parameters to the ParamsType class and set any default values
- Edit the `design_view_yourplugin.py` file to add new input fields to the submission dialog window and pass the values to the workflow

Please refer to the **video tutorial above** starting at 25:09 for a step-by-step walkthrough.

See the built-in [OVO design pages](https://github.com/MSDLLCpapers/ovo/tree/develop/ovo/app/pages/designs) for inspiration.

Please refer to [Nextflow documentation](https://www.nextflow.io/docs/latest/) for instructions how to build Nextflow workflows
and the [Streamlit documentation](https://docs.streamlit.io/) for more information on how to develop Streamlit apps.

</details>

&nbsp;

#### Part 3: Developing a generative "design" plugin for OVO

OVO distinguishes between two types of workflows, 
"descriptor" workflows that analyze existing designs 
and "design" workflows that generate new protein sequences and structures.

Developing a "design" plugin is similar to developing a "descriptor" plugin, but it is more complex 
because it requires implementing (typically) multi-step and multi-dependency Nextflow workflows, 
and processing logic to create new Design objects in the OVO database 
based on the workflow results, and a more advanced UI for submission.

A video tutorial and `ovo init plugin` template for developing a "design" plugin is coming soon. Please use the [Discussions tab](https://github.com/MSDLLCpapers/ovo/discussions)
for questions and support regarding plugin development.
