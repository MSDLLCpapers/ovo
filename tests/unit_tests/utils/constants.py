from enum import Enum
import os

TIMEOUT = 15
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
OVO_PAGES = os.path.join(REPO_ROOT, "ovo", "app", "pages")

JOBS_FILE = os.path.join(OVO_PAGES, "jobs", "jobs.py")
BULK_SUBMISSION_FILE = os.path.join(OVO_PAGES, "bulk", "bulk_submission.py")
SCAFFOLD_DESIGN_FILE = os.path.join(OVO_PAGES, "rfdiffusion", "scaffold_design.py")
BINDER_DESIGN_FILE = os.path.join(OVO_PAGES, "rfdiffusion", "binder_design.py")
EXPORT_FILE = os.path.join(OVO_PAGES, "export.py")
DESIGNS_FILE = os.path.join(OVO_PAGES, "designs", "designs.py")
