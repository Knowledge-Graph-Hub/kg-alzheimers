#!/bin/bash
# filepath: make_humanized_graph.sh

set -e

# Check if data directory and required files exist
if [ ! -d "data" ]; then
    echo "Error: 'data' directory not found"
    exit 1
fi

EDGES_FILE="data/kg-alzheimers_edges.tsv"
NODES_FILE="data/kg-alzheimers_nodes.tsv"
OUTPUT_FILE="data/kg-alzheimers_humanized_edges.tsv"

# Set limit for debugging - if 0 or empty, process all edges
DEBUG_LIMIT=${1:-0}

if [ ! -f "$EDGES_FILE" ]; then
    echo "Error: '$EDGES_FILE' not found"
    exit 1
fi

if [ ! -f "$NODES_FILE" ]; then
    echo "Error: '$NODES_FILE' not found"
    exit 1
fi

echo "Loading node names into memory..."

# Create a file for the node mapping in the data directory
NODE_MAP_FILE="data/node_mapping.tmp"

# Extract node ID to name mapping - get the id and name columns
NAME_COL=$(head -1 "$NODES_FILE" | tr '\t' '\n' | grep -n "name" | cut -d':' -f1)
ID_COL=$(head -1 "$NODES_FILE" | tr '\t' '\n' | grep -n "^id$" | cut -d':' -f1)
if [ -z "$NAME_COL" ]; then
    echo "Error: Could not find 'name' column in nodes file"
    exit 1
fi
if [ -z "$ID_COL" ]; then
    echo "Error: Could not find 'id' column in nodes file"
    exit 1
fi

echo "In nodes file: ID column is $ID_COL, Name column is $NAME_COL"

# Extract ID to name mapping - using proper field separator for TSV
awk -F'\t' -v id_col="$ID_COL" -v name_col="$NAME_COL" 'NR>1 {print $id_col "\t" $name_col}' "$NODES_FILE" > "$NODE_MAP_FILE"

# Find subject and object columns in the edge file
SUBJECT_COL=$(head -1 "$EDGES_FILE" | tr '\t' '\n' | grep -n "^subject$" | cut -d':' -f1)
OBJECT_COL=$(head -1 "$EDGES_FILE" | tr '\t' '\n' | grep -n "^object$" | cut -d':' -f1)
PREDICATE_COL=$(head -1 "$EDGES_FILE" | tr '\t' '\n' | grep -n "^predicate$" | cut -d':' -f1)
SOURCE_COL=$(head -1 "$EDGES_FILE" | tr '\t' '\n' | grep -n "^primary_knowledge_source$" | cut -d':' -f1)

if [ -z "$SUBJECT_COL" ] || [ -z "$OBJECT_COL" ] || [ -z "$PREDICATE_COL" ]; then
    echo "Error: Could not find required columns in edges file"
    echo "Looking for 'subject', 'object', and 'predicate' columns"
    exit 1
fi

if [ -z "$SOURCE_COL" ]; then
    echo "Warning: Could not find 'primary_knowledge_source' column in edges file"
    echo "The source information will not be included in the output"
fi

echo "In edges file: Subject column is $SUBJECT_COL, Predicate column is $PREDICATE_COL, Object column is $OBJECT_COL"
if [ -n "$SOURCE_COL" ]; then
    echo "Knowledge source column is $SOURCE_COL"
fi

# Create header for the output file - human-readable fields plus source
if [ -n "$SOURCE_COL" ]; then
    echo -e "subject\tpredicate\tobject\tsource" > "$OUTPUT_FILE"
else
    echo -e "subject\tpredicate\tobject" > "$OUTPUT_FILE"
fi

# Function to humanize the predicate
humanize_predicate() {
    local pred=$1
    
    # Check if it's a URI with prefix like "biolink:is_sequence_variant_of"
    if [[ $pred == *:* ]]; then
        # Strip prefix and convert underscores to spaces
        local human_pred=$(echo $pred | sed 's/.*://' | sed 's/_/ /g')
        echo "$human_pred"
    else
        # If it's an ID, look it up in the node map
        local pred_name=$(grep "^$pred"$'\t' "$NODE_MAP_FILE" | cut -f2)
        # If not found, return original
        if [ -z "$pred_name" ]; then
            echo "$pred"
        else
            echo "$pred_name"
        fi
    fi
}

# Function to humanize the source
humanize_source() {
    local source=$1
    
    # Check if it's a URI with prefix like "infores:clinvar"
    if [[ $source == *:* ]]; then
        # Strip prefix
        local human_source=$(echo $source | sed 's/.*://')
        echo "$human_source"
    else
        echo "$source"
    fi
}

# Show debug info
if [ "$DEBUG_LIMIT" -gt 0 ]; then
    echo "Processing first $DEBUG_LIMIT edges (debug mode)..."
    limit_msg="First $DEBUG_LIMIT"
else
    echo "Processing all edges (production mode)..."
    limit_msg="All"
fi

# Process edges and replace IDs with names
if [ -n "$SOURCE_COL" ]; then
    # Define the AWK command based on the DEBUG_LIMIT
    if [ "$DEBUG_LIMIT" -gt 0 ]; then
        awk_cmd="awk -F'\t' -v limit=$DEBUG_LIMIT -v subject_col=\"$SUBJECT_COL\" -v predicate_col=\"$PREDICATE_COL\" \
            -v object_col=\"$OBJECT_COL\" -v source_col=\"$SOURCE_COL\" 'NR>1 && NR<=(limit+1) {
                print \$subject_col \"\t\" \$predicate_col \"\t\" \$object_col \"\t\" \$source_col
            }' \"$EDGES_FILE\""
    else
        awk_cmd="awk -F'\t' -v subject_col=\"$SUBJECT_COL\" -v predicate_col=\"$PREDICATE_COL\" \
            -v object_col=\"$OBJECT_COL\" -v source_col=\"$SOURCE_COL\" 'NR>1 {
                print \$subject_col \"\t\" \$predicate_col \"\t\" \$object_col \"\t\" \$source_col
            }' \"$EDGES_FILE\""
    fi
    
    # Execute the AWK command and process the results
    eval $awk_cmd | while IFS=$'\t' read -r subject_id predicate object_id source; do
        subject_name=$(grep "^$subject_id"$'\t' "$NODE_MAP_FILE" | cut -f2)
        object_name=$(grep "^$object_id"$'\t' "$NODE_MAP_FILE" | cut -f2)
        
        # If names weren't found, keep the original IDs
        if [ -z "$subject_name" ]; then
            subject_name=$subject_id
        fi
        
        if [ -z "$object_name" ]; then
            object_name=$object_id
        fi
        
        # Humanize the predicate and source
        predicate_human=$(humanize_predicate "$predicate")
        source_human=$(humanize_source "$source")
        
        # Output with source information
        echo -e "$subject_name\t$predicate_human\t$object_name\t$source_human" >> "$OUTPUT_FILE"
    done
else
    # Define the AWK command based on the DEBUG_LIMIT
    if [ "$DEBUG_LIMIT" -gt 0 ]; then
        awk_cmd="awk -F'\t' -v limit=$DEBUG_LIMIT -v subject_col=\"$SUBJECT_COL\" -v predicate_col=\"$PREDICATE_COL\" \
            -v object_col=\"$OBJECT_COL\" 'NR>1 && NR<=(limit+1) {
                print \$subject_col \"\t\" \$predicate_col \"\t\" \$object_col
            }' \"$EDGES_FILE\""
    else
        awk_cmd="awk -F'\t' -v subject_col=\"$SUBJECT_COL\" -v predicate_col=\"$PREDICATE_COL\" \
            -v object_col=\"$OBJECT_COL\" 'NR>1 {
                print \$subject_col \"\t\" \$predicate_col \"\t\" \$object_col
            }' \"$EDGES_FILE\""
    fi
    
    # Execute the AWK command and process the results
    eval $awk_cmd | while IFS=$'\t' read -r subject_id predicate object_id; do
        subject_name=$(grep "^$subject_id"$'\t' "$NODE_MAP_FILE" | cut -f2)
        object_name=$(grep "^$object_id"$'\t' "$NODE_MAP_FILE" | cut -f2)
        
        # If names weren't found, keep the original IDs
        if [ -z "$subject_name" ]; then
            subject_name=$subject_id
        fi
        
        if [ -z "$object_name" ]; then
            object_name=$object_id
        fi
        
        # Humanize the predicate
        predicate_human=$(humanize_predicate "$predicate")
        
        # Output without source information
        echo -e "$subject_name\t$predicate_human\t$object_name" >> "$OUTPUT_FILE"
    done
fi

# Clean up
rm "$NODE_MAP_FILE"

echo "$limit_msg humanized edges have been saved to $OUTPUT_FILE"