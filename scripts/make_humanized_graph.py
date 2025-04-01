#!/usr/bin/env python3
"""
Humanize Knowledge Graph edges by replacing IDs with human-readable names.
Usage: python3 make_humanized_graph.py [debug_limit]
"""

import sys
import csv
from pathlib import Path

def find_column_index(header, pattern):
    """Find the index of a column in the header that matches the pattern."""
    for i, col in enumerate(header):
        if col == pattern:
            return i
    return -1

def humanize_predicate(pred, id_to_name):
    """Humanize a predicate by removing prefixes and converting underscores to spaces."""
    if ':' in pred:
        # Strip prefix and convert underscores to spaces
        return pred.split(':', 1)[1].replace('_', ' ')
    elif pred in id_to_name:
        return id_to_name[pred]
    return pred

def humanize_source(source):
    """Humanize a source by removing prefixes."""
    if ':' in source:
        return source.split(':', 1)[1]
    return source

def main():
    # Parse debug limit if provided
    debug_limit = 0
    if len(sys.argv) > 1:
        try:
            debug_limit = int(sys.argv[1])
        except ValueError:
            print(f"Invalid debug limit: {sys.argv[1]}")
            sys.exit(1)
    
    # File paths
    data_dir = Path("data")
    edges_file = data_dir / "kg-alzheimers_edges.tsv"
    nodes_file = data_dir / "kg-alzheimers_nodes.tsv"
    output_file = data_dir / "kg-alzheimers_humanized_edges.tsv"
    
    # Check if files exist
    if not data_dir.exists():
        print(f"Error: '{data_dir}' directory not found")
        sys.exit(1)
    if not edges_file.exists():
        print(f"Error: '{edges_file}' not found")
        sys.exit(1)
    if not nodes_file.exists():
        print(f"Error: '{nodes_file}' not found")
        sys.exit(1)
    
    print("Loading node names into memory...")
    
    # Find column indices in nodes file
    with open(nodes_file, 'r') as f:
        nodes_header = next(csv.reader(f, delimiter='\t'))
    
    id_col_idx = find_column_index(nodes_header, "id")
    name_col_idx = find_column_index(nodes_header, "name")
    
    if id_col_idx == -1:
        print("Error: Could not find 'id' column in nodes file")
        sys.exit(1)
    if name_col_idx == -1:
        print("Error: Could not find 'name' column in nodes file")
        sys.exit(1)
    
    print(f"In nodes file: ID column is {id_col_idx+1}, Name column is {name_col_idx+1}")
    
    # Find column indices in edges file
    with open(edges_file, 'r') as f:
        edges_header = next(csv.reader(f, delimiter='\t'))
    
    subject_col_idx = find_column_index(edges_header, "subject")
    predicate_col_idx = find_column_index(edges_header, "predicate")
    object_col_idx = find_column_index(edges_header, "object")
    source_col_idx = find_column_index(edges_header, "primary_knowledge_source")
    
    if subject_col_idx == -1 or predicate_col_idx == -1 or object_col_idx == -1:
        print("Error: Could not find required columns in edges file")
        print("Looking for 'subject', 'object', and 'predicate' columns")
        sys.exit(1)
    
    has_source = source_col_idx != -1
    
    if not has_source:
        print("Warning: Could not find 'primary_knowledge_source' column in edges file")
        print("The source information will not be included in the output")
    
    print(f"In edges file: Subject column is {subject_col_idx+1}, "
          f"Predicate column is {predicate_col_idx+1}, "
          f"Object column is {object_col_idx+1}")
    
    if has_source:
        print(f"Knowledge source column is {source_col_idx+1}")
    
    # Load node ID to name mapping
    id_to_name = {}
    with open(nodes_file, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        next(reader)  # Skip header
        for row in reader:
            if len(row) > max(id_col_idx, name_col_idx):
                node_id = row[id_col_idx]
                node_name = row[name_col_idx]
                if node_id:
                    id_to_name[node_id] = node_name
    
    print(f"Loaded {len(id_to_name)} node mappings")
    
    # Show mode info
    if debug_limit > 0:
        print(f"Processing first {debug_limit} edges (debug mode)...")
        limit_msg = f"First {debug_limit}"
    else:
        print("Processing all edges (production mode)...")
        limit_msg = "All"
    
    # Create header for the output file
    with open(output_file, 'w', newline='') as f_out:
        writer = csv.writer(f_out, delimiter='\t')
        if has_source:
            writer.writerow(["subject", "predicate", "object", "source"])
        else:
            writer.writerow(["subject", "predicate", "object"])
    
    # Process edges file
    count = 0
    with open(edges_file, 'r') as f_in, open(output_file, 'a', newline='') as f_out:
        reader = csv.reader(f_in, delimiter='\t')
        writer = csv.writer(f_out, delimiter='\t')
        next(reader)  # Skip header, we've already written it
        
        for row in reader:
            if debug_limit > 0 and count >= debug_limit:
                break
            
            if len(row) > max(subject_col_idx, predicate_col_idx, object_col_idx):
                subject_id = row[subject_col_idx]
                predicate = row[predicate_col_idx]
                object_id = row[object_col_idx]
                
                # Look up names
                subject_name = id_to_name.get(subject_id, subject_id)
                object_name = id_to_name.get(object_id, object_id)
                
                # Humanize predicate
                predicate = humanize_predicate(predicate, id_to_name)
                
                if has_source and len(row) > source_col_idx:
                    source = row[source_col_idx]
                    source = humanize_source(source)
                    writer.writerow([subject_name, predicate, object_name, source])
                else:
                    writer.writerow([subject_name, predicate, object_name])
            
            count += 1
    
    print(f"Processed {count} edges")
    print(f"{limit_msg} humanized edges have been saved to {output_file}")

if __name__ == "__main__":
    main()