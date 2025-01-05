import config
import os
import shutil
import sys


def copy_files(file_list, target_directory, overwrite=False):
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


def move_templates_to_plugin():
    if not os.path.isdir(config.DIR_GENERATED_LIVE_TEMPLATES):
        print("Directory with generated live templates does not exist.")
        sys.exit(1)

    if not os.path.isdir(config.DIR_PLUGIN_RESOURCE_FOLDER):
        print("Plugin resource folder does not exist.")
        sys.exit(1)

    files_and_dirs = os.listdir(config.DIR_GENERATED_LIVE_TEMPLATES)

    # Create a list of full file paths
    full_paths = [
        os.path.join(config.DIR_GENERATED_LIVE_TEMPLATES, file_or_dir)
        for file_or_dir in files_and_dirs
    ]

    copy_files(full_paths, config.DIR_PLUGIN_RESOURCE_FOLDER, overwrite=True)

    print("Successfully copied templates to plugin resource folder.")
