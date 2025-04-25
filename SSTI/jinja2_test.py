#!/usr/bin/env python3
import sys
import os
from jinja2 import Environment, FileSystemLoader, Template


def render_template(template, is_file=False):
    """Render a Jinja2 template without parameters"""
    try:
        if os.path.isfile(template):
            # Load template from file in the current directory
            env = Environment(loader=FileSystemLoader('.'))
            template = env.get_template(template)
        else:
            # Use template string directly
            template = Template(template)
        return template.render().strip()  # No parameters passed
    except Exception as e:
        return str(e)

def main():
    # Check if template source is provided
    if len(sys.argv) < 2:
        print("Usage: python jinja_test.py <template string or file> [--file]")
        print("Examples:")
        print(f"  python jinja_test.py '{{7+7}}'")
        sys.exit(1)

    # Get template source
    template = sys.argv[1]

    # Render and print the result
    result = render_template(template)
    print(result)

if __name__ == "__main__":
    main()
