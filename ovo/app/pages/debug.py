import subprocess
import streamlit as st
import ast
from io import StringIO
import yaml
from ovo import Design, Pool, Project, DesignJob, DescriptorJob, Round
from ovo import db, get_username, config
from ovo.app.utils.page_init import initialize_page

initialize_page(page_title="Debug")

st.title("🖥️ Debug")

st.write("This page is visible only to selected admin users.")

st.subheader("Run shell command")
with st.form(key="run_command", border=False):
    shell_command = st.text_area("Enter command:", placeholder="ls -la", key="shell_command", height=80)
    if st.form_submit_button("Run"):
        with st.spinner("Running command..."):
            result = subprocess.run(
                shell_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                shell=True,
            )
        st.write("Finished with output:" if result.returncode == 0 else "Finished with error:")
        st.code(result.stdout)

st.subheader("Run python command")
with st.form(key="run_python", border=False):
    python_command = st.text_area(
        "Enter command:", key="python_command", placeholder='pool = db.get(Pool, "abc");\nprint(pool.name)', height=150
    )
    if st.form_submit_button("Run"):
        with st.spinner("Running command..."):
            result = subprocess.run(
                f"""
                python <<EOF
from ovo import *
{python_command}
EOF
                """,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                shell=True,
            )
            st.write("Command:")
            st.code(python_command, language="python")
        st.write("Finished with output:" if result.returncode == 0 else "Finished with error:")
        st.code(result.stdout)

st.subheader("Session state")

st.write(st.session_state)

st.subheader("Config")

s = StringIO()
yaml.dump(config.model_dump(), s, sort_keys=False)
s.seek(0)
st.code(s.getvalue())

st.subheader("Database")

st.write("#### Projects")
kwargs = st.text_input("Filter JSON", placeholder='{"name": "Personal project"}', key="project_kwargs")
try:
    kwargs = ast.literal_eval(kwargs)
except:
    if kwargs:
        st.warning("Invalid kwargs format. Please enter a valid dictionary.")
    kwargs = {}
project_df = db.select_dataframe(model=Project, limit=1000, **kwargs)
st.dataframe(project_df)

st.write("#### Rounds")
kwargs = st.text_input("Filter JSON", key="rounds_kwargs")
try:
    kwargs = ast.literal_eval(kwargs)
except:
    if kwargs:
        st.warning("Invalid kwargs format. Please enter a valid dictionary.")
    kwargs = {}
rounds_df = db.select_dataframe(model=Round, limit=1000, **kwargs)
st.dataframe(rounds_df)

st.write("#### Pools")
kwargs = st.text_input("Filter JSON", placeholder=f'{{"author": "{get_username()}"}}', key="pool_kwargs")
try:
    kwargs = ast.literal_eval(kwargs)
except:
    if kwargs:
        st.warning("Invalid kwargs format. Please enter a valid dictionary.")
    kwargs = {}
pool_df = db.select_dataframe(model=Pool, limit=1000, **kwargs)
st.dataframe(pool_df)

st.write("#### Designs")
kwargs = st.text_input("Filter JSON", placeholder='{"name": "Personal project"}', key="design_kwargs")
try:
    kwargs = ast.literal_eval(kwargs)
except:
    if kwargs:
        st.warning("Invalid kwargs format. Please enter a valid dictionary.")
    kwargs = {}
design_df = db.select_dataframe(model=Design, limit=1000, **kwargs)
st.dataframe(design_df)

with st.expander("View design"):
    selected_design = st.selectbox("Select design", design_df.itertuples(), index=None, format_func=lambda x: x[0])
    if selected_design:
        design = db.select(model=Design, id=selected_design.Index)
        st.write(design)

st.write("#### Design jobs")
kwargs = st.text_input("Filter JSON", placeholder='{"job_result": True}', key="design_job_kwargs")
try:
    kwargs = ast.literal_eval(kwargs)
except:
    if kwargs:
        st.warning("Invalid kwargs format. Please enter a valid dictionary.")
    kwargs = {}
design_job_df = db.select_dataframe(model=DesignJob, limit=1000, **kwargs)
st.dataframe(design_job_df)

st.write("#### Descriptor jobs")
kwargs = st.text_input("Filter JSON", placeholder='{"job_result": True}', key="descriptor_job_kwargs")
try:
    kwargs = ast.literal_eval(kwargs)
except:
    if kwargs:
        st.warning("Invalid kwargs format. Please enter a valid dictionary.")
    kwargs = {}
descriptor_job_df = db.select_dataframe(model=DescriptorJob, limit=10000, **kwargs)
st.dataframe(descriptor_job_df)
