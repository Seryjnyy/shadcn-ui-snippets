import config
import json
import os
import re
import argparse
import sys
from pathlib import Path


def get_file_name_from_path(file_path):
    return os.path.basename(file_path)


def get_doc_files_from_dir(directory):
    print("Checking directory...")

    path = Path(directory)
    if not path.is_dir():
        print(f"Error: '{directory}' is not a valid directory.")
        sys.exit(1)

    doc_files = []
    for item in path.iterdir():
        if item.is_file() and (
            item.suffix == ".md" or item.suffix == ".mdx" or item.suffix == ".txt"
        ):  # Check for .md, .txt, or .mdx file
            doc_files.append(item)

    print(f"Doc files found in '{directory}':")
    for doc_file in doc_files:
        print(doc_file)

    return doc_files


def extract_code_blocks(text):
    # Regular expression to match content between code blocks, ignoring any metadata
    pattern = r"```(?:[^\n]*\n)(.*?)```"
    # re.DOTALL allows . to match newlines
    matches = re.findall(pattern, text, re.DOTALL)
    return [match.strip() for match in matches]


def remove_extension(text):
    return text.split(".")[0]


def parse_component_doc_file(doc_file_path):
    print(f"Parsing {doc_file_path}")

    with open(doc_file_path, "r", encoding="utf-8") as test:
        content = test.read()

        # Regular expression to get the Usage section of the doc
        pattern = r"## Usage\s+([\s\S]*?)(\n##|\Z)"
        match = re.search(pattern, content)

        if match:
            usage_section = match.group(1).strip()  # Extract and trim the Usage section

            code_blocks = extract_code_blocks(usage_section)

            imports = []
            usage = []

            # The usage section should have the first code block to show the import code
            # Then the next code block should be the example
            # In some cases it's not like that and it needs to be excluded from this process
            for block in code_blocks:
                if "import" in block:
                    # This will not work as expected with multiple imports (it will include all of them)
                    imports.append(block.strip())
                else:
                    usage.append(block.strip())

            output_file = f"{remove_extension(get_file_name_from_path(test.name))}.json"
            output_dir = "auto-defaults"

            os.makedirs(output_dir, exist_ok=True)

            print(
                f"Writing {output_file} contents to {os.path.join(output_dir, output_file)}"
            )
            with open(
                os.path.join(output_dir, output_file), "w", encoding="utf-8"
            ) as write_file:
                data = {
                    "name": remove_extension(
                        get_file_name_from_path(test.name)
                    ),  # duplicate code
                    "import": imports[0],
                    "usage": usage[0],
                }
                json.dump(data, write_file, indent=2, ensure_ascii=True)

                # for block in imports:
                #     write_file.write("$IMPORT$\n")
                #     write_file.write(block + "\n")

                # write_file.write("\n")
                # for index, block in enumerate(components):
                #     write_file.write(f"$USAGE$\n")
                #     write_file.write(block + "\n")

        else:
            print(f"No Usage section found for {get_file_name_from_path(test.name)}.")


def parse_component_doc_file(doc_file_path):
    print(f"Parsing {doc_file_path}")
    try:
        with open(doc_file_path, "r", encoding="utf-8") as test:
            content = test.read()

            # Regular expression to get the Usage section of the doc
            # pattern = r"## Usage\s+([\s\S]*?)(\n##|\Z)"
            # match = re.search(pattern, content)
            # usage_section = match.group(1).strip()  # Extract and trim the Usage section

            code_blocks = extract_code_blocks(content)

            if len(code_blocks) != 2:
                print("WRONG AMOUNT OF CODE BLOCKS")
                print(code_blocks)
                return False

            # now we now it has 2 code blocks

            # check if each code block has expected content
            # import starts with import ends with " or ";
            # usage has some code

            import_code_block = code_blocks[0]
            usage_code_block = code_blocks[1]

            if len(import_code_block) == 0:
                valid = import_code_block.startswith("import") and (
                    import_code_block.endswith('"') or import_code_block.endswith('";')
                )
                if not valid:
                    print(f"IMPROPER IMPORT: {get_file_name_from_path(test.name)}")
                    return False

            if len(usage_code_block) == 0:
                print(f"NO USAGE CODE: {get_file_name_from_path(test.name)}")
                return False

            output_file = f"{remove_extension(get_file_name_from_path(test.name))}.json"

            os.makedirs(config.DIR_GENERATED_JSONS, exist_ok=True)

            print(
                f"Writing {output_file} contents to {os.path.join(config.DIR_GENERATED_JSONS, output_file)}"
            )
            with open(
                os.path.join(config.DIR_GENERATED_JSONS, output_file),
                "w",
                encoding="utf-8",
            ) as write_file:
                data = {
                    "name": remove_extension(
                        get_file_name_from_path(test.name)
                    ),  # duplicate code
                    "import": import_code_block,
                    "usage": usage_code_block,
                }
                json.dump(data, write_file, indent=2, ensure_ascii=True)

    except Exception as e:
        print(f"Failed to parse {doc_file_path}", e)


def clean_directory(directory_path):

    try:
        # Loop over all items in the directory
        for filename in os.listdir(directory_path):
            file_path = os.path.join(directory_path, filename)

            # Check if it's a file (not a directory)
            if os.path.isfile(file_path):
                os.remove(file_path)  # Remove the file
                print(f"Deleted file: {file_path}")
            # Optionally, you can also check for directories and remove files inside
            # elif os.path.isdir(file_path):
            #     clean_directory(file_path)  # Recursively clean subdirectories
        print(f"Directory cleaned: {directory_path}")
    except Exception as e:
        print(f"Error cleaning directory: {e}")


def filter_unique_filenames(paths1, paths2):
    seen_filenames = {}  # Maps filename to its full path
    unique_paths = []
    duplicate_paths = []

    # Combine both path arrays
    all_paths = paths1 + paths2

    for path in all_paths:
        filename = os.path.basename(path)

        if filename not in seen_filenames:
            # First time seeing this filename
            seen_filenames[filename] = path
            unique_paths.append(path)
        else:
            # We've seen this filename before
            duplicate_paths.append(path)

    return unique_paths, duplicate_paths


def extract_defaults():
    auto_docs = get_doc_files_from_dir(config.DIR_AUTO_DOCS)
    manual_docs = get_doc_files_from_dir(config.DIR_MANUAL_DOCS)

    # check for duplicates
    # exit if duplicates file names, sort it out!
    unique_filepaths, duplicate_filepaths = filter_unique_filenames(
        auto_docs, manual_docs
    )

    if len(duplicate_filepaths) > 0:
        print("THERE ARE DUPLICATE DOCS FOR")
        print(duplicate_filepaths)

    # Clean output directory
    clean_directory(config.DIR_GENERATED_JSONS)

    # Parse and create JSON from each doc
    for x in unique_filepaths:
        parse_component_doc_file(x)


# Needs argument for output destination
# def main():
# parser = argparse.ArgumentParser(
#     prog="ExtractDefaults",
#     description="Extract the defaults (import and component) from a shadcn/ui component doc.",
#     epilog="",
# )

# parser.add_argument(
#     "-t",
#     "--target",
#     help="The folder path containing the component docs. Also, you can target a selection of files using -tf instead. It is required to only provide either a folder path or a list of file paths, but not both.",
# )
# parser.add_argument(
#     "-tf",
#     "--target-files",
#     help="The file paths of component docs you want to process specifically. Also, you can target the entire folder using -t instead. It is required to only provide either a folder path or a list of file paths, but not both.",
# )

# parser.add_argument(
#     "--dont-overwrite-output",
#     help="Chose if to not overwrite existing files in the output folder with the new versions. By default the files with the same name will be overwritten.",
#     action="store_true",
# )
# args = parser.parse_args()

# if not args.target and not args.target_files:
#     parser.error(f"You need to provide a directory.")
#     # Not implemented yet
#     # parser.error(f"You need to provide either a folder or file paths.")

# if args.target and args.target_files:
#     parser.error(
#         f"Please only provide either option but not both at the same time."
#     )

# if args.target:


# Filter out these as they need manual intervention
# exclude = set(
#     [
#         "aspect-ratio",
#         "calendar",
#         "chart",
#         "combobox",
#         "data-table",
#         "date-picker",
#         "form",
#         # radio group
#         "sidebar",
#         # sonner
#         "toast",
#         "typography",
#     ]
# )
# filtered = [
#     x
#     for x in res
#     if remove_extension(get_file_name_from_path(x)) not in exclude
# ]

# clean_directory(output_dir)
# print(len(docs))
# for x in manual_docs + auto_docs:
#     print(remove_extension(get_file_name_from_path(x)))
# parse_component_doc_file(x)

# if args.target_files:
#     print("Sorry not yet supported.")


# if __name__ == "__main__":
#     main()

# py ./scripts/extract-defaults.py -t ../shadcn-ui-repo/apps/www/content/docs/components
