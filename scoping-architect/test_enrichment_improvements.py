"""
Test script to verify enrichment improvements
"""
import json
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from architecture_designer.scoping_metadata_extractor import extract_scoping_metadata

# Load the latest enriched JSON
with open("outputs/20260615_221731_the_system/architecture_enriched.json") as f:
    enriched_json = json.load(f)

# Extract scoping metadata with improvements
scoping_metadata = extract_scoping_metadata(enriched_json)

# Display fill summary
print("\n" + "="*80)
print("ENRICHMENT IMPROVEMENT TEST RESULTS")
print("="*80)

fill_summary = scoping_metadata["fill_summary"]
print(f"\n📊 Fill Summary:")
print(f"   Total fields:  {fill_summary['total_fields']}")
print(f"   Auto-filled:   {fill_summary['auto_filled']}")
print(f"   Estimated:     {fill_summary['estimated']}")
print(f"   Needs input:   {fill_summary['needs_input']}")
print(f"   Fill rate:     {fill_summary['fill_rate_pct']}%")

# Show improvements in key areas
print(f"\n🎯 Key Improvements:")

# Users
users = scoping_metadata["users"]
print(f"\n   Users:")
for key in ["employees", "core_users", "self_service_users", "end_users", "target_trainees"]:
    if key in users:
        val = users[key]["value"]
        conf = users[key]["confidence"]
        print(f"      {key}: {val} ({conf})")

# Data Migration
data_mig = scoping_metadata["data_migration"]
print(f"\n   Data Migration:")
print(f"      no_of_data_objects: {data_mig['no_of_data_objects']['value']} ({data_mig['no_of_data_objects']['confidence']})")

# Testing
testing = scoping_metadata["testing"]
print(f"\n   Testing:")
for key in ["automation_scenarios_sap_gui", "automation_scenarios_fiori", "sit_scenarios_creation", "sit_scenarios_execution"]:
    if key in testing:
        val = testing[key]["value"]
        conf = testing[key]["confidence"]
        print(f"      {key}: {val} ({conf})")

# List fields still needing input
print(f"\n⚠️  Fields Still Needing Input:")
needs_input_fields = []

def find_needs_input(node, path=""):
    if isinstance(node, dict):
        if "confidence" in node and node["confidence"] == "needs-input":
            needs_input_fields.append(f"   {path}: {node.get('hint', 'No hint')}")
        else:
            for k, v in node.items():
                if not k.startswith("_"):
                    find_needs_input(v, f"{path}.{k}" if path else k)

find_needs_input(scoping_metadata)
for field in needs_input_fields[:15]:  # Show first 15
    print(field)

if len(needs_input_fields) > 15:
    print(f"   ... and {len(needs_input_fields) - 15} more")

print("\n" + "="*80)
print(f"✅ Target: >70% fill rate")
print(f"✅ Achieved: {fill_summary['fill_rate_pct']}%")
if fill_summary['fill_rate_pct'] > 70:
    print(f"🎉 SUCCESS! Exceeded target by {fill_summary['fill_rate_pct'] - 70:.1f}%")
else:
    print(f"⚠️  Need {70 - fill_summary['fill_rate_pct']:.1f}% more to reach target")
print("="*80 + "\n")

# Save enhanced output
output_path = "outputs/20260615_221731_the_system/architecture_enriched_v2.json"
enriched_json["scoping_metadata"] = scoping_metadata
with open(output_path, "w") as f:
    json.dump(enriched_json, f, indent=2)

print(f"💾 Enhanced output saved to: {output_path}\n")

# Made with Bob
