#!/usr/bin/env python3
import json
from pathlib import Path


def convert_segstats_to_ttl(segstats_path, output_path, subject_id, study_nidm_path=None):
    """
    Convert a segstats JSON file to TTL format
    """
    # Read the segstats JSON file
    with open(segstats_path, 'r') as f:
        data = json.load(f)
    
    # Create TTL content
    ttl_lines = []
    
    # Add prefixes
    ttl_lines.extend([
        "@prefix nidm: <http://purl.org/nidash/nidm#> .",
        "@prefix prov: <http://www.w3.org/ns/prov#> .",
        "@prefix dct: <http://purl.org/dc/terms/> .",
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .",
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
        "@prefix sio: <http://semanticscience.org/resource/> .",
        ""
    ])
    
    # Create a unique ID for this measurement
    measurement_id = f"fsl_{subject_id}_segmentation"
    
    # Add measurement data
    ttl_lines.append(f"nif:StatCollection_{measurement_id}")
    ttl_lines.append("    a nidm:Segmentation ;")
    ttl_lines.append(f"    dct:isPartOf <{subject_id}> ;")
    ttl_lines.append(f"    prov:wasGeneratedBy <fsl_segmentation_method> ;")
    ttl_lines.append("    rdfs:label \"FSL Segmentation Statistics\" ;")
    
    # Add each region's measurements
    for region, values in data.items():
        voxels = values.get('voxels', 0)
        volume_ml = values.get('volume_ml', 0.0)
        
        # Create a unique identifier for this region measurement
        region_safe = region.replace('-', '_').replace('.', '_')
        ttl_lines.append(f"    nidm:hasRegionMeasurements [")
        ttl_lines.append(f"        a nidm:AnatomicalSegment ;")
        ttl_lines.append(f"        sio:SIO_000332 \"{region}\" ;")
        ttl_lines.append(f"        nidm:volumeVoxels \"{voxels}\"^^xsd:decimal ;")
        ttl_lines.append(f"        nidm:volume_ml \"{volume_ml}\"^^xsd:decimal ;")
        ttl_lines.append(f"        prov:wasAttributedTo <{subject_id}> ;")
        ttl_lines.append(f"    ] ;")
    
    ttl_lines.append("    .")
    ttl_lines.append("")  # Empty line at the end
    
    # Ensure output directory exists
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write TTL content to file
    with open(output_path, 'w') as f:
        f.write('\n'.join(ttl_lines))


def main():
    base_dir = Path(".")
    
    # Process all subjects
    for i in range(1, 51):
        sub = f"sub-{i:02d}"
        segstats_path = base_dir / "derivatives" / "fsl" / sub / "ses-01" / "segstats.json"
        output_path = base_dir / "derivatives" / "fsl" / sub / "fsl_nidm.ttl"
        
        if segstats_path.exists():
            print(f"Converting {segstats_path.name} for {sub}...")
            convert_segstats_to_ttl(segstats_path, output_path, sub)
            print(f"Saved to {output_path}")
        else:
            print(f"Warning: {segstats_path} does not exist")


if __name__ == "__main__":
    main()
