#!/usr/bin/env python3
import random
import string

def generate_uuid():
    return ''.join(random.choices(string.hexdigits.lower(), k=8)) + '-' + ''.join(random.choices(string.hexdigits.lower(), k=4)) + '-' + ''.join(random.choices(string.hexdigits.lower(), k=4)) + '-' + ''.join(random.choices(string.hexdigits.lower(), k=4)) + '-' + ''.join(random.choices(string.hexdigits.lower(), k=12))

def get_sex(subject_id):
    sub_num = int(subject_id.split('-')[1])
    return 'M' if sub_num >= 26 else 'F'

def generate_fsl_values(subject_id):
    random.seed(hash(subject_id) % (2**32))
    sex = get_sex(subject_id)
    
    mean_vol = 4500
    std_vol = mean_vol * 0.05
    base_putamen_vol = max(0, random.gauss(mean_vol, std_vol))
    left_putamen_voxels_base = int(base_putamen_vol / 4) + random.gauss(0, 50)
    
    if sex == 'M':
        left_putamen_vol = round(base_putamen_vol * 1.05, 2)
        left_putamen_voxels = int(left_putamen_voxels_base * 1.05)
    else:
        left_putamen_vol = round(base_putamen_vol, 2)
        left_putamen_voxels = int(left_putamen_voxels_base)
    
    base = 172900000
    metrics = [
        (base, 1000), (375000000, 500000), (275, 225), (600, 500),
        (700, 500), (1750, 1250), (3000, 1000), (5500, 1500),
        (2500, 1000), (5000, 2000), (1000, 500), (2000, 1500),
        (left_putamen_voxels, 1), (left_putamen_vol, 1), (5750, 1750),
        (12500, 3500), (200, 100), (500, 300), (800, 400),
        (1400, 600), (2750, 750), (5250, 1250), (2600, 600),
        (5500, 1000), (1000, 300), (2250, 750), (3250, 750),
        (7000, 1500), (6000, 1500), (13000, 3500),
        (300000, 100000), (300000, 100000), (650000, 150000),
        (650000, 150000), (600000, 150000), (600000, 150000),
    ]
    
    return {
        'fsl:fsl_000001': round(metrics[0][0] + metrics[0][1] * random.gauss(0, 1), 0),
        'fsl:fsl_000002': round(metrics[1][0] + metrics[1][1] * random.gauss(0, 1), 1),
        'fsl:fsl_000003': int(round(metrics[2][0] + metrics[2][1] * random.gauss(0, 1), 0)),
        'fsl:fsl_000004': round(metrics[3][0] + metrics[3][1] * random.gauss(0, 1), 2),
        'fsl:fsl_000005': int(round(metrics[4][0] + metrics[4][1] * random.gauss(0, 1), 0)),
        'fsl:fsl_000006': round(metrics[5][0] + metrics[5][1] * random.gauss(0, 1), 2),
        'fsl:fsl_000007': int(round(metrics[6][0] + metrics[6][1] * random.gauss(0, 1), 0)),
        'fsl:fsl_000008': round(metrics[7][0] + metrics[7][1] * random.gauss(0, 1), 2),
        'fsl:fsl_000009': int(round(metrics[8][0] + metrics[8][1] * random.gauss(0, 1), 0)),
        'fsl:fsl_000010': round(metrics[9][0] + metrics[9][1] * random.gauss(0, 1), 2),
        'fsl:fsl_000011': int(round(metrics[10][0] + metrics[10][1] * random.gauss(0, 1), 0)),
        'fsl:fsl_000012': round(metrics[11][0] + metrics[11][1] * random.gauss(0, 1), 2),
        'fsl:fsl_000013': left_putamen_voxels,
        'fsl:fsl_000014': left_putamen_vol,
        'fsl:fsl_000015': int(round(metrics[14][0] + metrics[14][1] * random.gauss(0, 1), 0)),
        'fsl:fsl_000016': round(metrics[15][0] + metrics[15][1] * random.gauss(0, 1), 2),
        'fsl:fsl_000017': int(round(metrics[16][0] + metrics[16][1] * random.gauss(0, 1), 0)),
        'fsl:fsl_000018': round(metrics[17][0] + metrics[17][1] * random.gauss(0, 1), 2),
        'fsl:fsl_000019': int(round(metrics[18][0] + metrics[18][1] * random.gauss(0, 1), 0)),
        'fsl:fsl_000020': round(metrics[19][0] + metrics[19][1] * random.gauss(0, 1), 2),
        'fsl:fsl_000021': int(round(metrics[20][0] + metrics[20][1] * random.gauss(0, 1), 0)),
        'fsl:fsl_000022': round(metrics[21][0] + metrics[21][1] * random.gauss(0, 1), 2),
        'fsl:fsl_000023': int(round(metrics[22][0] + metrics[22][1] * random.gauss(0, 1), 0)),
        'fsl:fsl_000024': round(metrics[23][0] + metrics[23][1] * random.gauss(0, 1), 2),
        'fsl:fsl_000025': int(round(metrics[24][0] + metrics[24][1] * random.gauss(0, 1), 0)),
        'fsl:fsl_000026': round(metrics[25][0] + metrics[25][1] * random.gauss(0, 1), 2),
        'fsl:fsl_000027': int(round(metrics[26][0] + metrics[26][1] * random.gauss(0, 1), 0)),
        'fsl:fsl_000028': round(metrics[27][0] + metrics[27][1] * random.gauss(0, 1), 2),
        'fsl:fsl_000029': int(round(metrics[28][0] + metrics[28][1] * random.gauss(0, 1), 0)),
        'fsl:fsl_000030': round(metrics[29][0] + metrics[29][1] * random.gauss(0, 1), 2),
        'fsl:fsl_000031': int(round(metrics[30][0] + metrics[30][1] * random.gauss(0, 1), 0)),
        'fsl:fsl_000032': int(round(metrics[31][0] + metrics[31][1] * random.gauss(0, 1), 0)),
        'fsl:fsl_000033': int(round(metrics[32][0] + metrics[32][1] * random.gauss(0, 1), 0)),
        'fsl:fsl_000034': int(round(metrics[33][0] + metrics[33][1] * random.gauss(0, 1), 0)),
        'fsl:fsl_000035': int(round(metrics[34][0] + metrics[34][1] * random.gauss(0, 1), 0)),
        'fsl:fsl_000036': int(round(metrics[35][0] + metrics[35][1] * random.gauss(0, 1), 0)),
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
