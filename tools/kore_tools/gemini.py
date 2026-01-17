"""
Gemini prompt generator for Kore language spec improvements.
"""

from pathlib import Path


def _read_spec_folder() -> str:
    """Read all files from kore/spec folder with proper tags."""
    spec_dir = Path(__file__).parent.parent.parent / "kore" / "spec"

    if not spec_dir.exists():
        return "(spec folder not found)"

    contents = []
    for file in sorted(spec_dir.glob("*")):
        if file.is_file():
            try:
                text = file.read_text(encoding="utf-8")
                # Use filename without extension as tag name
                tag = file.stem.lower()
                contents.append(f"<{tag}>\n{text}\n</{tag}>")
            except Exception:
                pass

    return "\n".join(contents) if contents else "(no spec files found)"


REQUIREMENT = "REQUIREMENT"


def generate_prompts(requirement: str = REQUIREMENT) -> str:
    """
    Generate a prompt for Gemini to improve Kore spec.
    """
    spec_content = _read_spec_folder()

    context = """Anh đang thiết kế ngôn ngữ Kore - một ngôn ngữ lập trình để biểu diễn tư duy thành minh họa (illustrations) và chuyển động (animations).

Bên dưới là spec hiện tại của Kore."""

    prompt = f"""{context}

# Yêu cầu

{requirement}

<spec>
{spec_content}
</spec>"""

    return prompt


def main():
    """CLI entry point."""
    import subprocess
    import sys

    prompt = generate_prompts()

    # Copy to clipboard (macOS)
    try:
        subprocess.run(["pbcopy"], input=prompt.encode(), check=True)
        print("Copied to clipboard!")
    except Exception:
        # Fallback: print to stdout
        print(prompt, file=sys.stderr)
        print("(Failed to copy to clipboard)", file=sys.stderr)


if __name__ == "__main__":
    main()
