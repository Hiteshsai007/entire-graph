"""Normalize raw graph impact JSON into NormalizedFacts."""

from __future__ import annotations

from graphguard.engine.models import NormalizedFacts


def normalize_impact(raw: dict, symbol: str) -> NormalizedFacts:
    """Convert raw entire graph impact JSON into NormalizedFacts."""
    focus = raw.get("focus", {})
    file_path = focus.get("file_path", "")
    is_public = not symbol.startswith("_") and "tests/" not in file_path
    
    facts = NormalizedFacts(
        symbol=symbol,
        is_public=is_public,
        file_path=file_path,
        line=focus.get("start_line", 0),
    )

    # Entire Graph makes incomplete analysis machine-readable. Preserve that
    # signal instead of presenting relationship-derived output as authoritative.
    partial_failures = raw.get("partial_failures", [])
    for failure in partial_failures:
        code = failure.get("code", "partial failure") if isinstance(failure, dict) else str(failure)
        facts.analysis_limitations.append(f"partial failure: {code}")

    stats = raw.get("stats", {})
    completeness_level = stats.get("completeness_level")
    if completeness_level and completeness_level != "ok":
        facts.analysis_limitations.append(f"completeness level: {completeness_level}")

    scope = raw.get("completeness_scope", {})
    scope_level = scope.get("level")
    if scope_level and scope_level != "ok":
        facts.analysis_limitations.append(f"scope level: {scope_level}")

    if facts.analysis_limitations:
        facts.analysis_status = "partial"
    
    callers = raw.get("callers", {})
    
    # direct and transitive callers (count all entries)
    for entry in callers.get("entries", []):
        ep = entry.get("endpoint", {})
        name = ep.get("name", "")
        depth = entry.get("depth", 1)
        ep_file = ep.get("file_path", "")
        is_test = ep_file.startswith("test") or "tests/" in ep_file or "test_" in name
        
        if depth == 1:
            facts.raw_direct_callers += 1
            if not is_test:
                facts.direct_callers += 1
                if name not in facts.direct_caller_names:
                    facts.direct_caller_names.append(name)
        else:
            facts.raw_transitive_callers += 1
            if not is_test:
                facts.transitive_callers += 1
                if name not in facts.transitive_caller_names:
                    facts.transitive_caller_names.append(name)
                
        if is_test:
            if name not in facts.test_names:
                facts.test_names.append(name)
            previous_depth = facts.test_depths.get(name)
            if previous_depth is None or depth < previous_depth:
                facts.test_depths[name] = depth
                via = entry.get("via")
                if via:
                    facts.test_vias[name] = via
                else:
                    facts.test_vias.pop(name, None)

    # Calculate reachable tests as the number of unique test files
    test_files = set()
    for entry in callers.get("entries", []):
        ep = entry.get("endpoint", {})
        ep_file = ep.get("file_path", "")
        name = ep.get("name", "")
        is_test = ep_file.startswith("test") or "tests/" in ep_file or "test_" in name
        if is_test and ep_file:
            test_files.add(ep_file)
            
    facts.reachable_tests = len(test_files)
                    
    co_changes = raw.get("co_changes", {})
    facts.cochange_files = co_changes.get("total", 0)
    for entry in co_changes.get("entries", []):
        f = entry.get("file", "")
        if f:
            facts.cochange_file_names.append(f)
            
    callees = raw.get("callees", {})
    for entry in callees.get("entries", []):
        name = entry.get("endpoint", {}).get("name")
        if name and name not in facts.callees:
            facts.callees.append(name)
            
    type_consumers = raw.get("type_consumers", {})
    for entry in type_consumers.get("entries", []):
        name = entry.get("endpoint", {}).get("name")
        if name and name not in facts.type_consumers:
            facts.type_consumers.append(name)
            
    siblings = raw.get("siblings", {})
    for entry in siblings.get("entries", []):
        name = entry.get("endpoint", {}).get("name")
        if name and name not in facts.siblings:
            facts.siblings.append(name)
            
    # Add blind spots
    lang = focus.get("language", "")
    if lang in ["Text", "Markdown", "JSON", "YAML", "TOML"]:
        facts.blind_spots.append("inventory-only language")
    
    if "getattr" in str(raw).lower() or "dynamic dispatch" in str(raw).lower() or "reflection" in str(raw).lower():
        # Heuristic for the demo
        facts.blind_spots.append("reflection/getattr")
    
    return facts
