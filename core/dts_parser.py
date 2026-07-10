import re

def parse_dts_nodes(content: str) -> dict[str, list[str]]:
    """
    Parses DTS/DTSI content and groups properties/subnode lines by their full node path.
    Handles single-line overlays and nested node syntax.
    """
    node_data = {}
    stack = []
    
    # Matches patterns like: &i2c1 { or temperature@48 { or / {
    node_start_re = re.compile(r'([&/\w\-@:]+)\s*\{')
    
    lines = content.splitlines()
    in_multiline_comment = False
    
    for line in lines:
        raw_line = line.strip()
        if not raw_line:
            continue
            
        # Strip comments
        if in_multiline_comment:
            if "*/" in raw_line:
                raw_line = raw_line.split("*/", 1)[1].strip()
                in_multiline_comment = False
            else:
                continue
                
        if "/*" in raw_line:
            if "*/" in raw_line:
                raw_line = re.sub(r'/\*.*?\*/', '', raw_line).strip()
            else:
                raw_line = raw_line.split("/*", 1)[0].strip()
                in_multiline_comment = True
                
        if "//" in raw_line:
            raw_line = raw_line.split("//", 1)[0].strip()
            
        if not raw_line:
            continue
            
        # Match node declaration starts
        start_match = node_start_re.search(raw_line)
        if start_match:
            node_name = start_match.group(1)
            stack.append(node_name)
            current_path = "/".join(stack)
            if current_path not in node_data:
                node_data[current_path] = []
            
            # Check for inline single-line nodes: &node { prop = 1; };
            post_brace = raw_line.split("{", 1)[1].strip()
            if post_brace and post_brace != "}":
                if post_brace.endswith("};") or post_brace.endswith("}"):
                    prop_part = post_brace.rstrip("};").rstrip("}").strip().rstrip(";").strip()
                    if prop_part:
                        node_data[current_path].append(prop_part)
                    stack.pop()
            continue
            
        # Match node declaration ends
        if raw_line.startswith("};") or raw_line == "}":
            if stack:
                stack.pop()
            continue
            
        # Add property lines to the active node path
        if stack:
            current_path = "/".join(stack)
            prop_clean = raw_line.rstrip(";").strip()
            if prop_clean:
                node_data[current_path].append(prop_clean)
                
    return node_data

def get_modified_nodes(base_nodes: dict[str, list[str]], target_nodes: dict[str, list[str]]) -> set[str]:
    """
    Identifies the set of node paths that were added, removed, or modified
    between the base and target node dictionaries.
    """
    modified = set()
    
    # Check all target nodes (additions or property modifications)
    for node_path, target_props in target_nodes.items():
        base_props = base_nodes.get(node_path)
        if base_props is None:
            modified.add(node_path)
        else:
            if sorted(base_props) != sorted(target_props):
                modified.add(node_path)
                
    # Check for deleted nodes
    for node_path in base_nodes:
        if node_path not in target_nodes:
            modified.add(node_path)
            
    return modified
