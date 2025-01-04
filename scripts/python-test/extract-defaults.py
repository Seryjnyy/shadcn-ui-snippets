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
        if item.is_file() and (item.suffix == '.md' or item.suffix == '.mdx'):  # Check for .md or .mdx file
            doc_files.append(item)
    
    print(f"Markdown files found in '{directory}':")
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
    return text.split('.')[0]

def parse_component_doc_file(doc_file_path):
    print(f"Parsing {doc_file_path}")
    
    with open(doc_file_path, "r") as test:
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
            
            print(f"Writing {output_file} contents to {os.path.join(output_dir, output_file)}")
            with open(os.path.join(output_dir, output_file), "w") as write_file:
                data = {
                    "name":output_file,
                    "import":imports[0],
                    "usage":usage[0]
                }
                json.dump(data, write_file, indent=2,ensure_ascii=True)
                
                # for block in imports:
                #     write_file.write("$IMPORT$\n")
                #     write_file.write(block + "\n")
                    
                # write_file.write("\n")
                # for index, block in enumerate(components):
                #     write_file.write(f"$USAGE$\n")
                #     write_file.write(block + "\n")


        else:
            print(f"No Usage section found for {get_file_name_from_path(test.name)}.")
        



# Needs argument for output destination
def main():
    parser = argparse.ArgumentParser(
                    prog='ExtractDefaults',
                    description='Extract the defaults (import and component) from a shadcn/ui component doc.',
                    epilog='')

    parser.add_argument('-t', '--target', help="The folder path containing the component docs. Also, you can target a selection of files using -tf instead. It is required to only provide either a folder path or a list of file paths, but not both.")
    parser.add_argument('-tf', '--target-files', help="The file paths of component docs you want to process specifically. Also, you can target the entire folder using -t instead. It is required to only provide either a folder path or a list of file paths, but not both.")  
    
    parser.add_argument('--dont-overwrite-output', help="Chose if to not overwrite existing files in the output folder with the new versions. By default the files with the same name will be overwritten.", action="store_true")
    args = parser.parse_args()
    
    if not args.target and not args.target_files:
        parser.error(f"You need to provide a directory.")
        # Not implemented yet
        # parser.error(f"You need to provide either a folder or file paths.")
    
    if args.target and args.target_files:
        parser.error(f"Please only provide either option but not both at the same time.")

    if args.target:
        res = get_doc_files_from_dir(args.target)
        
        # Filter out these as they need manual intervention
        exclude = set(["form", "date-picker", "chart", "typography", "data-table", "combobox", "calendar", "toast", "sidebar", "aspect-ratio"])
        filtered = [x for x in res if remove_extension(get_file_name_from_path(x)) not in exclude]
        # for x in filtered:
        #     parse_component_doc_file(x)
        
    with open(os.path.join("auto-defaults", "avatar.json"), "r", encoding="utf-8") as test:    
        data = json.load(test)
        with open("testing.txt", "w") as test_write:
            test_write.write(data["usage"])
        
    if args.target_files:
        print("Sorry not yet supported.")
    
if __name__ == "__main__":
    main()

# py ./scripts/extract-defaults.py -t ../shadcn-ui-repo/apps/www/content/docs/components