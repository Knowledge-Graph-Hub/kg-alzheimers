#!/usr/bin/env python3
"""
Script to convert PubMed Central (PMC) XML files to text files.
Handles duplicate detection based on PMC IDs and extracts plain text from XML structure.
"""

import os
import argparse
from pathlib import Path
from bs4 import BeautifulSoup
from typing import Set, Dict, Optional
import logging
import re

def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def extract_pmc_id_from_filename(filename: str) -> Optional[str]:
    """Extract PMC ID from filename (e.g., 'PMC1234567.xml' -> 'PMC1234567')."""
    match = re.search(r'PMC\d+', filename)
    return match.group(0) if match else None

def extract_pmc_id_from_xml(xml_path: str) -> Optional[str]:
    """Extract PMC ID from XML content if available."""
    try:
        with open(xml_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, "lxml-xml")
        
        # Look for PMC ID in various places
        pmc_id_elem = soup.find("article-id", {"pub-id-type": "pmc"})
        if pmc_id_elem:
            pmc_id = pmc_id_elem.get_text(strip=True)
            if not pmc_id.startswith('PMC'):
                pmc_id = f'PMC{pmc_id}'
            return pmc_id
        
        return None
    except Exception as e:
        logging.warning(f"Could not extract PMC ID from {xml_path}: {e}")
        return None

def extract_plain_text_from_pmc_xml(xml_path: str) -> str:
    """
    Extract plain text from PMC XML file.
    
    Args:
        xml_path: Path to the XML file
        
    Returns:
        Extracted text content as string
    """
    try:
        with open(xml_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file, "lxml-xml")
    except Exception as e:
        logging.error(f"Failed to parse XML file {xml_path}: {e}")
        return f"Error parsing XML: {e}"

    sections = []

    # Title
    title = soup.find("article-title")
    if title:
        sections.append(f"# Title\n{title.get_text(strip=True)}")

    # Abstract
    abstract = soup.find("abstract")
    if abstract:
        paragraphs = [p.get_text(" ", strip=True) for p in abstract.find_all("p")]
        if paragraphs:
            sections.append(f"# Abstract\n{' '.join(paragraphs)}")

    # Main body sections
    body = soup.find("body")
    if body:
        for sec in body.find_all("sec", recursive=False):
            section_title = sec.find("title")
            section_header = f"## {section_title.get_text(strip=True)}" if section_title else "## Section"
            paragraphs = [p.get_text(" ", strip=True) for p in sec.find_all("p")]
            if paragraphs:
                sections.append(f"{section_header}\n" + "\n\n".join(paragraphs))

    # Conclusion/References section
    back = soup.find("back")
    if back:
        for sec in back.find_all("sec", recursive=False):
            section_title = sec.find("title")
            if section_title and "conclusion" in section_title.get_text(strip=True).lower():
                section_header = f"## {section_title.get_text(strip=True)}"
                paragraphs = [p.get_text(" ", strip=True) for p in sec.find_all("p")]
                if paragraphs:
                    sections.append(f"{section_header}\n" + "\n\n".join(paragraphs))

    result = "\n\n".join(sections) if sections else "No content extracted"
    return result

def find_xml_files(input_dir: str) -> list:
    """Find all XML files in the input directory."""
    xml_files = []
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.xml'):
                xml_files.append(os.path.join(root, file))
    return xml_files

def detect_duplicates(xml_files: list) -> Dict[str, list]:
    """
    Detect duplicate files based on PMC IDs.
    
    Args:
        xml_files: List of XML file paths
        
    Returns:
        Dictionary mapping PMC ID to list of file paths
    """
    pmc_to_files = {}
    files_without_pmc = []
    
    for xml_file in xml_files:
        # First try to get PMC ID from filename
        pmc_id = extract_pmc_id_from_filename(os.path.basename(xml_file))
        
        # If not found in filename, try to extract from XML content
        if not pmc_id:
            pmc_id = extract_pmc_id_from_xml(xml_file)
        
        if pmc_id:
            if pmc_id not in pmc_to_files:
                pmc_to_files[pmc_id] = []
            pmc_to_files[pmc_id].append(xml_file)
        else:
            files_without_pmc.append(xml_file)
    
    # Log files without PMC IDs
    if files_without_pmc:
        logging.warning(f"Found {len(files_without_pmc)} files without PMC IDs")
        for file in files_without_pmc:
            logging.debug(f"No PMC ID found for: {file}")
    
    return pmc_to_files

def convert_xml_to_text(input_dir: str, output_dir: str, handle_duplicates: bool = True) -> None:
    """
    Convert XML files to text files.
    
    Args:
        input_dir: Directory containing XML files
        output_dir: Directory to save text files
        handle_duplicates: Whether to handle duplicate detection
    """
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Find all XML files
    xml_files = find_xml_files(input_dir)
    logging.info(f"Found {len(xml_files)} XML files")
    
    if handle_duplicates:
        # Detect duplicates
        pmc_to_files = detect_duplicates(xml_files)
        
        # Report duplicates
        duplicates = {pmc_id: files for pmc_id, files in pmc_to_files.items() if len(files) > 1}
        if duplicates:
            logging.info(f"Found {len(duplicates)} PMC IDs with duplicates:")
            for pmc_id, files in duplicates.items():
                logging.info(f"  {pmc_id}: {len(files)} files")
                for file in files:
                    logging.debug(f"    {file}")
        
        # Process files (use first file for duplicates)
        processed_files = []
        for pmc_id, files in pmc_to_files.items():
            processed_files.append(files[0])  # Use first file
            if len(files) > 1:
                logging.debug(f"Using {files[0]} for {pmc_id}, skipping {len(files)-1} duplicates")
    else:
        processed_files = xml_files
    
    logging.info(f"Processing {len(processed_files)} files (after duplicate handling)")
    
    # Convert files
    successful = 0
    failed = 0
    
    for xml_file in processed_files:
        try:
            # Extract PMC ID for output filename
            pmc_id = extract_pmc_id_from_filename(os.path.basename(xml_file))
            if not pmc_id:
                pmc_id = extract_pmc_id_from_xml(xml_file)
            
            if not pmc_id:
                # Use original filename without extension
                pmc_id = Path(xml_file).stem
            
            # Extract text
            text_content = extract_plain_text_from_pmc_xml(xml_file)
            
            # Save to text file
            output_file = os.path.join(output_dir, f"{pmc_id}.txt")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text_content)
            
            successful += 1
            logging.debug(f"Converted: {xml_file} -> {output_file}")
            
        except Exception as e:
            failed += 1
            logging.error(f"Failed to convert {xml_file}: {e}")
    
    logging.info(f"Conversion complete: {successful} successful, {failed} failed")

def main():
    parser = argparse.ArgumentParser(description='Convert PMC XML files to text files')
    parser.add_argument('input_dir', help='Directory containing XML files')
    parser.add_argument('output_dir', help='Directory to save text files')
    parser.add_argument('--no-duplicates', action='store_true', 
                       help='Skip duplicate detection and process all files')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    
    if not os.path.exists(args.input_dir):
        logging.error(f"Input directory does not exist: {args.input_dir}")
        return 1
    
    handle_duplicates = not args.no_duplicates
    convert_xml_to_text(args.input_dir, args.output_dir, handle_duplicates)
    
    return 0

if __name__ == '__main__':
    exit(main())