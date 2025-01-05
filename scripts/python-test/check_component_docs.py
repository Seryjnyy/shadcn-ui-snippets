import re
import os
import config


TEMPLATE_DOC_USAGE_SECTION = """
```tsx
 
```

```tsx
 
```                    
"""


# duplicate code with extract
def extract_code_blocks(text):
    # Regular expression to match content between code blocks, ignoring any metadata
    pattern = r"```(?:[^\n]*\n)(.*?)```"
    # re.DOTALL allows . to match newlines
    matches = re.findall(pattern, text, re.DOTALL)
    return [match.strip() for match in matches]


def check_files_in_directory(directory_path):

    unsupported_files = []
    cant_find_usage_section_files = []

    good_files = []
    bad_files = []
    allowed_extensions = {".md", ".mdx", ".txt"}

    # Iterate through all files in the directory
    for filename in os.listdir(directory_path):
        usage_code_block_for_writing = ""
        print(f"Checking {filename}")
        file_path = os.path.join(directory_path, filename)
        # Skip directories
        if os.path.isdir(file_path):
            print(f"Skipping, {filename} is a directory.")
            continue

        # Get the file extension
        _, file_extension = os.path.splitext(filename)

        # Check if the file extension is allowed
        if file_extension not in allowed_extensions:
            unsupported_files.append(file_path)
            print(f"Skipping, {filename} because {file_extension} is not allowed.")
            bad_files.append((filename, file_path, "Unexpected file extension."))
            # Stop processing further for this file
            continue

        # Process file content
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                print(f"Checking content in {filename}")
                content = file.read()
                # duplicate code with extract
                pattern = r"## Usage\s+([\s\S]*?)(\n##|\Z)"
                match = re.search(pattern, content)
                if match:
                    usage_section = match.group(
                        1
                    ).strip()  # Extract and trim the Usage section
                    code_blocks = extract_code_blocks(usage_section)

                    if len(code_blocks) > 2:
                        # print(f"Error: too much, need manual check {filename}")
                        bad_files.append(
                            (filename, file_path, "Has more than 2 code blocks.")
                        )
                        continue
                    elif len(code_blocks) < 2:
                        bad_files.append(
                            (filename, file_path, "Has less than 2 code blocks.")
                        )
                        continue

                    # check if import is okay
                    # print(code_blocks[0])
                    # should only have one import string, should end with "

                    if code_blocks[0].count("import") > 1:
                        bad_files.append(
                            (
                                filename,
                                file_path,
                                "Import code block has more than one import.",
                            )
                        )
                        continue

                    if not code_blocks[0].endswith('"') and not code_blocks[0].endswith(
                        '";'
                    ):
                        bad_files.append(
                            (
                                filename,
                                file_path,
                                'Import code block does not end with expected " or "; char.',
                            )
                        )
                        continue

                    # component should start with < and end with >
                    # otherwise it needs manual check
                    usage_code_block = code_blocks[1]
                    if not usage_code_block.startswith(
                        "<"
                    ) or not usage_code_block.endswith(">"):
                        bad_files.append(
                            (
                                filename,
                                file_path,
                                "Usage code block is not a simple component.",
                            )
                        )
                        continue

                    good_files.append((filename, file_path, usage_section))
                else:
                    # print(f"Couldn't find Usage section in {filename}")
                    bad_files.append(
                        (filename, file_path, "Could not find Usage section.")
                    )
                    cant_find_usage_section_files.append(file_path)
                    continue

        except Exception as e:
            print(f"Error checking content in {filename}: {e}")

    print(f"BAD FILES {len(bad_files)}")
    for f in bad_files:
        print(f[0])
    print(f"GOOD FILES {len(good_files)}")
    for f in good_files:
        print(f[0])

    return good_files, bad_files


def create_doc_file(target_directory, filename, content="", overwrite=False):
    # Ensure the target directory exists
    os.makedirs(target_directory, exist_ok=True)
    # Construct the full file path
    file_path = os.path.join(target_directory, filename)

    if not os.path.exists(file_path) or overwrite:
        try:
            # Create the file
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)
            print(f"Created: {file_path}")
        except Exception as e:
            print(f"Error creating file {file_path}: {e}")
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted the file: {file_path}")
    else:
        print(f"File already exists, skipping: {file_path}")


# returns true if no manual intervention needed, false if needed
def check_and_generate_docs():
    # don't take a directory directly
    # just take the files
    # combine files from auto and manual
    # maybe have script to check how many components are on shadcn, then compare with how many we have
    #   like how many can be processed, how many snippets were generated

    good_files, bad_files = check_files_in_directory(config.DIR_DOCS_FROM_REPO)

    for file in good_files:
        create_doc_file(
            target_directory=config.DIR_AUTO_DOCS,
            filename=file[0],
            content=file[2],
            overwrite=False,
        )

    for file in bad_files:
        create_doc_file(
            target_directory=config.DIR_MANUAL_DOCS,
            filename=file[0],
            content=TEMPLATE_DOC_USAGE_SECTION,
            overwrite=False,
        )

    if len(bad_files) > 0:
        return False

    return True
