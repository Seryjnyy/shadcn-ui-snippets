import os
import subprocess
import config
import shutil

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


# duplicate code
def copy_files(file_list, target_directory, overwrite=False):
    """
    Copies a list of files to a target directory.

    :param file_list: List of file paths to copy.
    :param target_directory: Directory where files will be copied.
    """
    # Ensure the target directory exists
    os.makedirs(target_directory, exist_ok=True)

    for file_path in file_list:

        try:
            # Copy each file to the target directory
            if overwrite or not os.path.exists(
                os.path.join(target_directory, os.path.basename(file_path))
            ):
                shutil.copy(file_path, target_directory)
                print(f"Copied: {file_path} -> {target_directory}")
            else:
                print(f"File already exists: {file_path}")
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except Exception as e:
            print(f"Error copying {file_path}: {e}")


def move_from_repo_to_project():
    pathToDir = REPO_DIR + DIR_COMPONENTS_IN_REPO

    files_and_dirs = os.listdir(pathToDir)

    full_paths = [
        os.path.join(pathToDir, file_or_dir) for file_or_dir in files_and_dirs
    ]

    copy_files(full_paths, config.DIR_DOCS_FROM_REPO)
