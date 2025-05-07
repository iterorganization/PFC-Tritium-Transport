import os
import json

processed_data = []
results_dir = "results"

# Collect all results
for filename in os.listdir(results_dir):
    if filename.endswith(".json"):
        with open(os.path.join(results_dir, filename), "r") as f:
            processed_data.append(json.load(f))

# Save final merged data
with open("final_results.json", "w") as f:
    json.dump(processed_data, f, indent=4)

print("Merged all results into final_results.json")