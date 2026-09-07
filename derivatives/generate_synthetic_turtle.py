#!/usr/bin/env python3
"""Generate synthetic NIDM RDF Turtle data for 50 subjects with sex-based left putamen differences"""
import random
import string

def generate_uuid():
    return ''.join(random.choices(string.hexdigits.lower(), k=8)) + '-' + \
           ''.join(random.choices(string.hexdigits.lower(), k=4)) + '-' + \
           ''.join(random.choices(string.hexdigits.lower(), k=4)) + '-' + \
           ''.join(random.choices(string.hexdigits.lower(), k=4)) + '-' + \
           ''.join(random.choices(string.hexdigits.lower(), k=12))

def get_sex(subject_id):
    """Read sex from participants.tsv"""
    sub_num = int(subject_id.split('-')[1])
    # sub-01 to sub-25 are F, sub-26 to sub-50 are M
    return 'M' if sub_num >= 26 else 'F'

def generate_fsl_values(subject_id):
    """Generate synthetic FSL stats values"""
    random.seed(hash(subject_id) % (2**32))
    base = 172900000 + random.randint(0, 100000)
    sex = get_sex(subject_id)
    
    # Base left putamen values
    left_putamen_voxels_base = random.randint(2000, 3500)
    left_putamen_vol_base = round(4500 + random.uniform(0, 3000), 2)
    
    # Males have on average 5% larger left putamen
    if sex == 'M':
        # Multiply by 1.05
        left_putamen_voxels = int(left_putamen_voxels_base * 1.05)
        left_putamen_vol = round(left_putamen_vol_base * 1.05, 2)
    else:
        left_putamen_voxels = left_putamen_voxels_base
        left_putamen_vol = left_putamen_vol_base
    
    return {
        'fsl:fsl_000001': base + random.randint(0, 1000),
        'fsl:fsl_000002': round(375000000 + random.randint(0, 500000), 1),
        'fsl:fsl_000003': random.randint(50, 500),
        'fsl:fsl_000004': round(100 + random.uniform(0, 1000), 2),
        'fsl:fsl_000005': random.randint(200, 1200),
        'fsl:fsl_000006': round(500 + random.uniform(0, 2500), 2),
        'fsl:fsl_000007': random.randint(2000, 4000),
        'fsl:fsl_000008': round(4000 + random.uniform(0, 3000), 2),
        'fsl:fsl_000009': random.randint(1500, 3500),
        'fsl:fsl_000010': round(3000 + random.uniform(0, 4000), 2),
        'fsl:fsl_000011': random.randint(500, 1500),
        'fsl:fsl_000012': round(1000 + random.uniform(0, 3000), 2),
        'fsl:fsl_000013': left_putamen_voxels,
        'fsl:fsl_000014': left_putamen_vol,
        'fsl:fsl_000015': random.randint(4000, 7500),
        'fsl:fsl_000016': round(9000 + random.uniform(0, 7000), 2),
        'fsl:fsl_000017': random.randint(100, 300),
        'fsl:fsl_000018': round(200 + random.uniform(0, 600), 2),
        'fsl:fsl_000019': random.randint(400, 1200),
        'fsl:fsl_000020': round(800 + random.uniform(0, 2000), 2),
        'fsl:fsl_000021': random.randint(2000, 3500),
        'fsl:fsl_000022': round(4000 + random.uniform(0, 2500), 2),
        'fsl:fsl_000023': random.randint(2000, 3200),
        'fsl:fsl_000024': round(4500 + random.uniform(0, 2000), 2),
        'fsl:fsl_000025': random.randint(700, 1300),
        'fsl:fsl_000026': round(1500 + random.uniform(0, 1500), 2),
        'fsl:fsl_000027': random.randint(2500, 4000),
        'fsl:fsl_000028': round(5500 + random.uniform(0, 3000), 2),
        'fsl:fsl_000029': random.randint(4500, 7500),
        'fsl:fsl_000030': round(9500 + random.uniform(0, 7000), 2),
        'fsl:fsl_000031': random.randint(200000, 400000),
        'fsl:fsl_000032': random.randint(200000, 400000),
        'fsl:fsl_000033': random.randint(500000, 800000),
        'fsl:fsl_000034': random.randint(500000, 800000),
        'fsl:fsl_000035': random.randint(450000, 750000),
        'fsl:fsl_000036': random.randint(450000, 750000),
    }

def format_value(key, val):
    if key in ['fsl:fsl_000002', 'fsl:fsl_000004', 'fsl:fsl_000006', 'fsl:fsl_000008',
               'fsl:fsl_000010', 'fsl:fsl_000012', 'fsl:fsl_000014', 'fsl:fsl_000016',
               'fsl:fsl_000018', 'fsl:fsl_000020', 'fsl:fsl_000022', 'fsl:fsl_000024',
               'fsl:fsl_000026', 'fsl:fsl_000028', 'fsl:fsl_000030',
               'fsl:fsl_000032', 'fsl:fsl_000034', 'fsl:fsl_000036']:
        return f'"{val}"^^xsd:float'
    return str(val)

def generate_subject_block(subject_id, uuid=None):
    uuid = uuid or generate_uuid()
    activity_uuid = generate_uuid()
    agent_uuid = generate_uuid()
    subject_uuid = generate_uuid()
    
    values = generate_fsl_values(subject_id)
    
    lines = [
        f'niiri:{uuid} a nidm:FSLStatsCollection,',
        '        prov:Entity ;'
    ]
    for key, val in values.items():
        lines.append(f'    {key} {format_value(key, val)} ;')
    lines.append(f'    prov:wasGeneratedBy niiri:{activity_uuid} .')
    lines.append('')
    lines.append(f'niiri:{activity_uuid} a prov:Activity ;')
    lines.append('    dct:description "FSL FAST/FIRST segmentation statistics" ;')
    lines.append('    prov:qualifiedAssociation [ a prov:Association ;')
    lines.append(f'            prov:agent niiri:{agent_uuid} ;')
    lines.append('            prov:hadRole nidm:NIDM_0000164 ],')
    lines.append('        [ a prov:Association ;')
    lines.append(f'            prov:agent niiri:{subject_uuid} ;')
    lines.append('            prov:hadRole sio:Subject ] .')
    lines.append('')
    lines.append(f'niiri:{agent_uuid} a prov:Agent,')
    lines.append('        prov:SoftwareAgent ;')
    lines.append('    nidm:NIDM_0000164 fsl: .')
    lines.append('')
    lines.append(f'niiri:{subject_uuid} a prov:Agent ;')
    lines.append(f'    ndar:src_subject_id "{subject_id}"^^xsd:string .')
    lines.append('')
    
    return '\n'.join(lines)

def main():
    header = '''@prefix dct: <http://purl.org/dc/terms/> .
@prefix fsl: <http://purl.org/nidash/fsl#> .
@prefix ndar: <https://ndar.nih.gov/api/datadictionary/v2/dataelement/> .
@prefix nidm: <http://purl.org/nidash/nidm#> .
@prefix niiri: <http://iri.nidash.org/> .
@prefix prov: <http://www.w3.org/ns/prov#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix sio: <http://semanticscience.org/ontology/sio.owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

'''
    footer = '''fsl:DataElement rdfs:subClassOf nidm:DataElement .
'''
    
    subject_blocks = []
    for i in range(1, 51):
        subject_id = f'sub-{i:02d}'
        block = generate_subject_block(subject_id)
        subject_blocks.append(block)
    
    output = header + '\n'.join(subject_blocks) + footer
    
    with open('all_fsl_50subjects_sex_adjusted.ttl', 'w') as f:
        f.write(output)
    
    print("Generated all_fsl_50subjects_sex_adjusted.ttl")
    print("Males (sub-26 to sub-50) have 5% larger left putamen volume on average")

if __name__ == "__main__":
    main()
