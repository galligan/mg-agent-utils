#!/usr/bin/env python3
import json
import os
import argparse
from datetime import datetime, timezone
import sys
from difflib import SequenceMatcher
import re

def similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() > 0.7

def to_kebab_case(s):
    """Convert a string to kebab-case (lowercase with hyphens)"""
    # Convert to lowercase
    s = s.lower()
    # Replace spaces, underscores, slashes and other separators with hyphens
    s = re.sub(r'[\s_/]+', '-', s)
    # Remove any non-alphanumeric characters except hyphens and periods
    s = re.sub(r'[^\w\.-]', '', s)
    # Replace multiple consecutive hyphens with a single one
    s = re.sub(r'-+', '-', s)
    # Remove leading/trailing hyphens
    s = s.strip('-')
    return s

# Parse command line arguments
parser = argparse.ArgumentParser(description='Track and read rule usage analytics')
subparsers = parser.add_subparsers(dest='operation', required=True, help='Operation to perform')

# Write command
write_parser = subparsers.add_parser('write', help='Track rule usage by writing to analytics file')
write_parser.add_argument('--filename', required=True, help='The name of the rule file being used')
write_parser.add_argument('--by', dest='agent', required=True, help='The name of the agent being used')

# Read command
read_parser = subparsers.add_parser('read', help='Read usage analytics')
read_parser.add_argument('--sort', choices=['last', 'first', 'recent', 'name'], default='last', 
                        help='Sort by: last/recent usage (default), first usage, or name')
read_parser.add_argument('--filter', help='Filter by agent name (fuzzy search)')

# Rename command
rename_parser = subparsers.add_parser('rename', help='Rename a rule while preserving its history')
rename_parser.add_argument('old_name', help='The old name of the rule file')
rename_parser.add_argument('new_name', help='The new name of the rule file')

args = parser.parse_args()

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Analytics file path in the same directory as the script
analytics_file = os.path.join(script_dir, 'rules_analytics.json')
# Format timestamp to YYYY-MM-DD[T]HH:MM:SS[Z]
current_date = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

# Use dictionaries for faster lookups: rules keyed by filename, usage keyed by agent
def load_analytics(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                
                # Handle old format migration and structure cleanup
                if isinstance(data.get("rules"), list) or needs_structure_cleanup(data):
                    print("Migrating analytics format to optimized structure.")
                    new_rules = {}
                    
                    # Handle list-based format
                    rules_data = data.get("rules", []) if isinstance(data.get("rules"), list) else data.get("rules", {}).values()
                    
                    for rule in rules_data:
                        filename = rule.get("filename")
                        if filename:
                            new_usage = {}
                            
                            # Handle both list and dict usage formats
                            usage_items = rule.get("usage", []) if isinstance(rule.get("usage"), list) else rule.get("usage", {}).values()
                            
                            for usage in usage_items:
                                agent = usage.get("agent")
                                if agent:
                                    # Convert agent name to kebab-case
                                    agent_key = to_kebab_case(agent)
                                    # Remove redundant agent field if it matches the key
                                    new_usage[agent_key] = {
                                        "usageCount": usage.get("usageCount", 0),
                                        "firstUsed": usage.get("firstUsed", current_date),
                                        "lastUsed": usage.get("lastUsed", current_date)
                                    }
                            
                            # Preserve or initialize previousNames field
                            previous_names = rule.get("previousNames", [])
                            
                            # Don't store filename since it's the key
                            new_rules[filename] = {
                                "usage": new_usage,
                                "previousNames": previous_names
                            }
                    
                    data["rules"] = new_rules
                    # Save the migrated data immediately
                    save_analytics(filepath, data)
                
                return data
        except json.JSONDecodeError:
            print(f"Error: Could not parse {filepath}. Creating new structure.")
        except Exception as e:
            print(f"Error loading or migrating analytics data: {e}. Starting fresh.")
    return {"rules": {}} # Default to dictionary structure

def needs_structure_cleanup(data):
    """Check if the data structure has redundant fields that need cleanup"""
    if not isinstance(data.get("rules"), dict):
        return False
        
    for filename, rule in data.get("rules", {}).items():
        # Check if rule still has filename field
        if "filename" in rule:
            return True
            
        # Check if usage items still have agent field
        for agent_key, usage in rule.get("usage", {}).items():
            if "agent" in usage:
                return True
            
        # Check if previousNames field exists
        if "previousNames" not in rule:
            return True
                
    return False

def save_analytics(filepath, data):
     with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

analytics_data = load_analytics(analytics_file)

if args.operation == 'write':
    filename = args.filename
    # Convert agent name to kebab-case for consistency
    agent_key = to_kebab_case(args.agent)
    
    # Use dictionary access for rule entry
    rule_entry = analytics_data["rules"].get(filename)

    if not rule_entry:
        rule_entry = {
            "usage": {}, # Use dictionary for usage
            "previousNames": []  # Initialize previousNames array
        }
        analytics_data["rules"][filename] = rule_entry

    # Use dictionary access for agent usage entry
    agent_usage = rule_entry["usage"].get(agent_key)

    if not agent_usage:
        agent_usage = {
            "usageCount": 0,
            "firstUsed": current_date,
            "lastUsed": current_date
        }
        rule_entry["usage"][agent_key] = agent_usage

    # Update usage statistics
    agent_usage["usageCount"] += 1
    agent_usage["lastUsed"] = current_date

    # Write updated analytics data using the save function
    save_analytics(analytics_file, analytics_data)

    print(f'Analytics updated for rule "{filename}" used by "{args.agent}"')

elif args.operation == 'rename':
    old_name = args.old_name
    new_name = args.new_name
    
    # Check if the old name exists
    if old_name not in analytics_data["rules"]:
        print(f'Error: Rule "{old_name}" not found in analytics data.')
        sys.exit(1)
        
    # Check if the new name already exists
    if new_name in analytics_data["rules"]:
        print(f'Warning: Rule "{new_name}" already exists. Merging the history from "{old_name}".')
        
        # Copy usage data from old to new if agent doesn't exist in new
        for agent_key, old_usage in analytics_data["rules"][old_name]["usage"].items():
            if agent_key not in analytics_data["rules"][new_name]["usage"]:
                analytics_data["rules"][new_name]["usage"][agent_key] = old_usage
            else:
                # Agent exists in both - keep the one with earlier firstUsed
                old_first = datetime.fromisoformat(old_usage["firstUsed"])
                new_first = datetime.fromisoformat(analytics_data["rules"][new_name]["usage"][agent_key]["firstUsed"])
                
                if old_first < new_first:
                    analytics_data["rules"][new_name]["usage"][agent_key]["firstUsed"] = old_usage["firstUsed"]
                
                # Sum the usage counts
                analytics_data["rules"][new_name]["usage"][agent_key]["usageCount"] += old_usage["usageCount"]
                
                # Take the most recent lastUsed
                old_last = datetime.fromisoformat(old_usage["lastUsed"])
                new_last = datetime.fromisoformat(analytics_data["rules"][new_name]["usage"][agent_key]["lastUsed"])
                
                if old_last > new_last:
                    analytics_data["rules"][new_name]["usage"][agent_key]["lastUsed"] = old_usage["lastUsed"]
        
        # Initialize previousNames if it doesn't exist
        if "previousNames" not in analytics_data["rules"][new_name]:
            analytics_data["rules"][new_name]["previousNames"] = []
        
        # Add old name to previousNames if not already there
        if old_name not in analytics_data["rules"][new_name]["previousNames"]:
            analytics_data["rules"][new_name]["previousNames"].append(old_name)
        
        # Add old previousNames to new previousNames if not already there
        for prev_name in analytics_data["rules"][old_name].get("previousNames", []):
            if prev_name not in analytics_data["rules"][new_name]["previousNames"]:
                analytics_data["rules"][new_name]["previousNames"].append(prev_name)
    else:
        # Create new entry with old data
        analytics_data["rules"][new_name] = analytics_data["rules"][old_name].copy()
        
        # Initialize previousNames if it doesn't exist
        if "previousNames" not in analytics_data["rules"][new_name]:
            analytics_data["rules"][new_name]["previousNames"] = []
        
        # Add old name to previousNames
        if old_name not in analytics_data["rules"][new_name]["previousNames"]:
            analytics_data["rules"][new_name]["previousNames"].append(old_name)
    
    # Remove old entry
    del analytics_data["rules"][old_name]
    
    # Save changes
    save_analytics(analytics_file, analytics_data)
    print(f'Rule renamed from "{old_name}" to "{new_name}" while preserving history.')

elif args.operation == 'read':
    # Check if the rules dictionary is empty
    if not analytics_data.get("rules"):
        print("No analytics data found.")
        sys.exit(0)
    
    # Process data for display
    display_data = []
    # Iterate over the key-value pairs of the rules dictionary
    for filename, rule_entry in analytics_data["rules"].items():
        total_usage = 0
        rule_last_used_date = None
        rule_last_agent = None
        rule_first_used_date = None
        agent_match_found = not args.filter # True if no filter, False if filter needs matching
        previous_names = rule_entry.get("previousNames", [])

        # Iterate over the key-value pairs of the usage dictionary
        for agent_key, agent_usage in rule_entry["usage"].items():
            usage_count = agent_usage["usageCount"]
            
            # We'll use the agent_key for display since we no longer store the agent name
            agent_name = agent_key
            
            # Check filter first - convert filter to kebab-case to match our keys
            filter_key = to_kebab_case(args.filter) if args.filter else None
            is_match = not args.filter or similar(filter_key, agent_key)
            if args.filter and is_match:
                agent_match_found = True # Mark that at least one agent matched the filter for this rule

            # Only process stats if the agent matches the filter (or if no filter is applied)
            if is_match:
                total_usage += usage_count
                
                # Convert dates once
                try:
                    current_last_used = datetime.fromisoformat(agent_usage["lastUsed"])
                    current_first_used = datetime.fromisoformat(agent_usage["firstUsed"])
                except ValueError:
                    print(f"Warning: Skipping invalid date format for agent '{agent_name}' in rule '{filename}'")
                    continue # Skip this usage entry if dates are invalid

                # Update overall rule first/last usage dates based on matching agents
                if rule_last_used_date is None or current_last_used > rule_last_used_date:
                    rule_last_used_date = current_last_used
                    rule_last_agent = agent_name # Track the agent associated with the latest date *among matching agents*

                if rule_first_used_date is None or current_first_used < rule_first_used_date:
                    rule_first_used_date = current_first_used
        
        # Only add to display if a matching agent was found (or if no filter was applied)
        # and if we actually found valid usage dates
        if agent_match_found and rule_last_used_date:
            display_data.append({
                "filename": filename,
                "total_usage": total_usage, # Total usage from matching agents
                "last_agent": rule_last_agent, # Last agent among matching ones
                "last_used": rule_last_used_date, # Last date among matching ones
                "first_used": rule_first_used_date, # Earliest date among matching ones
                "previous_names": previous_names # Previous names of the rule
            })
    
    # Sort data
    if args.sort == 'name':
        display_data.sort(key=lambda x: x["filename"])
    elif args.sort == 'first':
        display_data.sort(key=lambda x: x["first_used"])
    else:  # 'last' or 'recent'
        display_data.sort(key=lambda x: x["last_used"], reverse=True)
    
    # Print table header
    has_prev_names = any(len(item["previous_names"]) > 0 for item in display_data)
    prev_names_col = " | Previous Names" if has_prev_names else ""
    print(f"{'Filename':<30} | {'Total Usage':<12} | {'Last Agent':<20} | {'Last Used':<25}{prev_names_col}")
    print("-" * (93 + (len(prev_names_col) if has_prev_names else 0)))
    
    # Print table data
    for item in display_data:
        prev_names_text = ", ".join(item["previous_names"]) if has_prev_names else ""
        prev_names_col = f" | {prev_names_text}" if has_prev_names else ""
        print(f"{item['filename']:<30} | {item['total_usage']:<12} | {item['last_agent']:<20} | {item['last_used'].strftime('%Y-%m-%d %H:%M:%S')}{prev_names_col}")
