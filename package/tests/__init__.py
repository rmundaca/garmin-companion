import os
import tempfile

# Isolated database and tokens for the whole suite (before importing app.*)
os.environ.setdefault("GC_DATA_DIR", tempfile.mkdtemp(prefix="gc-tests-"))
