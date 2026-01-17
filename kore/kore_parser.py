"""
Kore language parser.

Syntax:
    object NAME
      property: value

    animate NAME.action

    mindmap ROOT
      CHILD1
        GRANDCHILD1
      CHILD2

    save filename.gif
"""

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Object:
    name: str
    properties: dict = field(default_factory=dict)


@dataclass
class Animation:
    target: str
    action: str


@dataclass
class Save:
    filename: str


@dataclass
class Show:
    pass


@dataclass
class MindmapNode:
    text: str
    children: list = field(default_factory=list)
    depth: int = 0


@dataclass
class Mindmap:
    root: MindmapNode = None


@dataclass
class KoreProgram:
    objects: list[Object] = field(default_factory=list)
    animations: list[Animation] = field(default_factory=list)
    saves: list[Save] = field(default_factory=list)
    shows: list[Show] = field(default_factory=list)
    mindmaps: list[Mindmap] = field(default_factory=list)


class KoreParser:
    def _get_indent(self, line: str) -> int:
        """Get indentation level (number of 2-space indents)"""
        spaces = len(line) - len(line.lstrip())
        return spaces // 2

    def _parse_mindmap(self, lines: list, start_idx: int) -> tuple[Mindmap, int]:
        """Parse mindmap block, return (Mindmap, next_line_index)"""
        first_line = lines[start_idx]
        root_text = first_line.strip()[8:].strip()  # Remove "mindmap "
        root = MindmapNode(text=root_text, depth=0)
        mindmap = Mindmap(root=root)

        # Stack: [(node, indent_level)]
        stack = [(root, 0)]
        i = start_idx + 1

        while i < len(lines):
            line = lines[i]

            # Empty line ends mindmap block
            if not line.strip():
                break

            # Non-indented line (except save/show) ends mindmap block
            if not line.startswith(" ") and not line.strip().startswith("save") and not line.strip().startswith("show"):
                break

            # Check if it's a command (save, show, animate, object, mindmap)
            stripped = line.strip()
            if stripped.startswith(("save ", "show", "animate ", "object ", "mindmap ")):
                break

            # Parse child node
            indent = self._get_indent(line)
            text = stripped

            if indent > 0 and text:
                node = MindmapNode(text=text, depth=indent)

                # Find parent: pop stack until we find a node with smaller indent
                while stack and stack[-1][1] >= indent:
                    stack.pop()

                if stack:
                    parent = stack[-1][0]
                    parent.children.append(node)

                stack.append((node, indent))

            i += 1

        return mindmap, i

    def parse(self, source: str) -> KoreProgram:
        program = KoreProgram()
        lines = source.split("\n")

        current_object = None
        i = 0

        while i < len(lines):
            line = lines[i]
            stripped = line.strip()

            # Skip empty lines
            if not stripped:
                i += 1
                continue

            # Mindmap: mindmap ROOT
            if stripped.startswith("mindmap "):
                mindmap, i = self._parse_mindmap(lines, i)
                program.mindmaps.append(mindmap)
                current_object = None
                continue

            # Object definition: object NAME
            if stripped.startswith("object "):
                name = stripped[7:].strip()
                current_object = Object(name=name)
                program.objects.append(current_object)
                i += 1
                continue

            # Animation: animate TARGET.action
            if stripped.startswith("animate "):
                match = re.match(r"animate\s+(\w+)\.(\w+)", stripped)
                if match:
                    program.animations.append(Animation(
                        target=match.group(1),
                        action=match.group(2)
                    ))
                current_object = None
                i += 1
                continue

            # Save: save filename
            if stripped.startswith("save "):
                filename = stripped[5:].strip()
                program.saves.append(Save(filename=filename))
                current_object = None
                i += 1
                continue

            # Show: show (launch GUI)
            if stripped == "show":
                program.shows.append(Show())
                current_object = None
                i += 1
                continue

            # Property (indented, key: value)
            if current_object and line.startswith("  "):
                if ":" in stripped:
                    key, value = stripped.split(":", 1)
                    current_object.properties[key.strip()] = value.strip()
                i += 1
                continue

            i += 1

        return program

    def parse_file(self, path: str) -> KoreProgram:
        return self.parse(Path(path).read_text())
