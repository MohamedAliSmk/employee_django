import os
import django

# Set the settings module path (adjust this if your settings file is in a subfolder)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "employees_django.settings")

# Setup Django
django.setup()

# Dump data into a file
from django.core.management import call_command

with open("data.json", "w", encoding="utf-8") as f:
    call_command(
        "dumpdata",
        exclude=["contenttypes", "auth.Permission"],
        indent=2,
        stdout=f,
        use_natural_primary_keys=True,
        use_natural_foreign_keys=True,
    )
