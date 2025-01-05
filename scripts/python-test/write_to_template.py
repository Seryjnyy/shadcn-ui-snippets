import config
import xml.etree.ElementTree as ET
import os
import json
import argparse
from pathlib import Path
import sys


def create_template_xml(group, name, value, desc):
    # Create the root element
    root = ET.Element("templateSet", attrib={"group": group})

    # Add the 'template' child with attributes
    template = ET.SubElement(
        root,
        "template",
        attrib={
            "name": name,
            "value": value,
            "description": desc,
            "toReformat": "true",
            "toShortenFQNames": "true",
        },
    )
    print(template.get("value"))
    # Add the 'context' element
    context = ET.SubElement(template, "context")

    # Add 'option' elements
    ET.SubElement(context, "option", attrib={"name": "JavaScript", "value": "true"})
    ET.SubElement(context, "option", attrib={"name": "TypeScript", "value": "true"})

    # Create the XML tree
    tree = ET.ElementTree(root)

    # Write to file
    with open("template.xml", "wb", encoding="utf-8") as file:
        tree.write(file, encoding="utf-8", xml_declaration=False)


def escape_for_template(input_string):
    """
    Escapes <, >, and newlines in a given string for IntelliJ live templates.

    :param input_string: The input string to process.
    :return: The escaped string.
    """
    # Replace special characters
    escaped_string = input_string.replace("<", "&lt;").replace(">", "&gt;")
    # Replace newlines with &#10;, preserving indentation
    escaped_string = escaped_string.replace("\n", "&#10;")
    return escaped_string


def get_json_files_from_dir(directory):
    print("Checking directory...")

    path = Path(directory)
    if not path.is_dir():
        print(f"Error: '{directory}' is not a valid directory.")
        sys.exit(1)

    doc_files = []
    for item in path.iterdir():
        if item.is_file() and (item.suffix == ".json"):  # Check for .json file
            doc_files.append(item)

    print(f"JSON files found in '{directory}':")
    for doc_file in doc_files:
        print(doc_file)

    # TODO : should check if they are valid

    return doc_files


def create_snippet_xml(root, name, value, desc):
    # Add the 'template' child with attributes
    snippet = ET.SubElement(
        root,
        "template",
        attrib={
            "name": name,
            "value": value,
            "description": desc,
            "toReformat": "true",
            "toShortenFQNames": "true",
        },
    )

    # Add the 'context' element
    context = ET.SubElement(snippet, "context")

    # Add 'option' elements
    ET.SubElement(context, "option", attrib={"name": "JavaScript", "value": "true"})
    ET.SubElement(context, "option", attrib={"name": "TypeScript", "value": "true"})
    return snippet


def write_to_template():
    # parser = argparse.ArgumentParser(
    #     prog="ExtractDefaults",
    #     description="Extract the defaults (import and component) from a shadcn/ui component doc.",
    #     epilog="",
    # )

    # parser.add_argument(
    #     "-t",
    #     "--target",
    #     help="The folder path containing the parsed component docs (json).",
    #     required=True,
    # )

    # args = parser.parse_args()

    # jsons = get_json_files_from_dir(args.target)
    jsons = get_json_files_from_dir(config.DIR_GENERATED_JSONS)

    import_root = ET.Element("templateSet", attrib={"group": "shadcn/ui-imports"})
    usage_root = ET.Element("templateSet", attrib={"group": "shadcn/ui-usage"})

    for path in jsons:
        with open(path, "r", encoding="utf-8") as comp:
            data = json.load(comp)
            usage_code = data["usage"]
            import_code = data["import"]
            name = data["name"]
            desc = f"https://ui.shadcn.com/docs/components/{name}"
            create_snippet_xml(import_root, f"cni-{name}", import_code, desc)
            create_snippet_xml(usage_root, f"cnu-{name}", usage_code, desc)

    import_snippet_set = ET.ElementTree(import_root)
    usage_snippet_set = ET.ElementTree(usage_root)

    os.makedirs(config.DIR_GENERATED_LIVE_TEMPLATES, exist_ok=True)

    with open(
        os.path.join(
            config.DIR_GENERATED_LIVE_TEMPLATES, "shadcn-ui-import-snippets.xml"
        ),
        "wb",
    ) as file:
        import_snippet_set.write(file, encoding="utf-8", xml_declaration=False)

    with open(
        os.path.join(
            config.DIR_GENERATED_LIVE_TEMPLATES, "shadcn-ui-usage-snippets.xml"
        ),
        "wb",
    ) as file:
        usage_snippet_set.write(file, encoding="utf-8", xml_declaration=False)
