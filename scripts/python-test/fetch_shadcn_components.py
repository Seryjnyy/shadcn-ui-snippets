import os
import subprocess
import config

# Directory for the templates repo
REPO_DIR = "../shadcn-ui-repo"
REPO_URL = "https://github.com/shadcn-ui/ui.git"

DIR_COMPONENTS_IN_REPO = "/apps/www/content/docs/components"


def run_command(command, cwd=None):
    print(f"Running command: {' '.join(command)}")
    subprocess.run(command, cwd=cwd, check=True)


def fetch_shadcn_components():
    # Check if the directory exists
    if not os.path.exists(REPO_DIR):
        print("Cloning shadcn/ui repository...")

        # Clone in repo
        # With no checkout, and with only 1 level of history
        run_command(
            ["git", "clone", "--depth", "1", "--no-checkout", REPO_URL, REPO_DIR]
        )

        # Initialise sparse-checkout
        run_command(["git", "sparse-checkout", "init"], cwd=REPO_DIR)

        # Configure sparse-checkout
        # Replace old values with the folder we want
        only_include_this_content = DIR_COMPONENTS_IN_REPO + "/*"
        with open(
            os.path.join(REPO_DIR, ".git", "info", "sparse-checkout"), "w"
        ) as sparse_file:
            print("Updating sparse-checkout configuration.")
            sparse_file.write(only_include_this_content)

        # Checkout the main branch to finally pull in the files
        run_command(["git", "checkout", "main"], cwd=REPO_DIR)
    else:
        print("Repository exists. Pulling latest changes...")
        run_command(["git", "-C", REPO_DIR, "pull"], cwd=REPO_DIR)

print("Repository is up to date.")