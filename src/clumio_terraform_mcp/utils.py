# Template-based config generation using Jinja2.

import jinja2
from pathlib import Path

def render_tf_template(template_name: str, **context) -> str:
    """Convenience function to render a Terraform template.

    Args:
        template_name: Name of the template file
        **context: Variables to pass to the template
        
    Returns:
        Rendered Terraform configuration as string
    """
    template_dir = Path(__file__).parent / "templates"

    environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(template_dir)),
        trim_blocks=False,
        lstrip_blocks=False,
    )
    template = environment.get_template(template_name)
    return template.render(**context)
