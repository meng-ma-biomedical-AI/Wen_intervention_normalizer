from intervention_normalizer import configure
import os


def get_map():
    drug_types = "T200"
    chemical_types = "T116,T195,T123,T122,T103,T120,T104,T196,T126,T131,T125,T129,T130,T197,T114,T109,T121,T192,T127"
    procedure_types = "T060,T065,T058,T059,T063,T062,T061"
    device_types = "T203,T074,T075"
    activity_types = "T052,T053,T056,T051,T064,T055,T066,T057,T054"
    sem_map = {}

    for item in drug_types.split(','):
        sem_map[item] = 'drug'
    for item in chemical_types.split(','):
        sem_map[item] = 'chemical'
    for item in procedure_types.split(','):
        sem_map[item] = 'procedure'
    for item in device_types.split(','):
        sem_map[item] = 'device'
    for item in activity_types.split(','):
        sem_map[item] = 'activity'
    return sem_map


def get_semtype_id(file):
    sem_id = {}
    with open(file, 'r') as f:
        for line in f:
            tokens = line.split('|')
            sem_id[tokens[3]] = tokens[2]
    return sem_id


def convert2standard(snippets):
    sem_id = get_semtype_id(os.path.join(configure.RESOURCE_PATH, 'SemGroups.txt'))
    sem_map = get_map()

    for snippet in snippets:
        drug = []
        chemical = []
        procedure = []
        device = []
        activity = []
        components = []
        for entity in snippet['entities']:
            components.append(entity['cui'])
            temp_entity = {'text': entity['ngram'], 'maps_to': entity['cui'] + ':' + entity['term']}

            ent_types = {sem_id[item] for item in entity['semtypes']}
            valid_types = ent_types & sem_map.keys()

            if "T200" in valid_types:
                sem_type = 'drug'
            else:
                valid_types = list(valid_types)
                sem_type = sem_map[valid_types[0]]

            del entity['ngram']
            del entity['term']
            del entity['cui']
            del entity['similarity']
            del entity['semtypes']
            del entity['preferred']
            del entity['id']

            for key, value in entity.items():
                temp_entity[key] = value

            if sem_type == 'drug':
                drug.append(temp_entity)
            elif sem_type == 'chemical':
                chemical.append(temp_entity)
            elif sem_type == 'procedure':
                procedure.append(temp_entity)
            elif sem_type == 'device':
                device.append(temp_entity)
            elif sem_type == 'activity':
                activity.append(temp_entity)

        if len(drug) > 0:
            snippet['has_drug'] = drug
        if len(chemical) > 0:
            snippet['has_chemical'] = chemical
        if len(procedure) > 0:
            snippet['has_procedure'] = procedure
        if len(device) > 0:
            snippet['has_device'] = device
        if len(activity) > 0:
            snippet['has_activity'] = activity

        del snippet['entities']
        del snippet['processed']
        del snippet['representation']

        # add the relation
        if snippet['relation'] == 'N/A':
            relation = 'N/A'
        elif snippet['relation'] == 'combined_with':
            comp = '<->'.join(components)
            relation = 'combined_with (' + comp + ')'
        elif snippet['relation'] == 'before':
            comp = '->'.join(components)
            relation = 'before (' + comp + ')'
        elif snippet['relation'] == 'after':
            comp = '->'.join(reversed(components))
            relation = 'before (' + comp + ')'
        elif snippet['relation'] == 'contain':
            comp = '->'.join(components)
            relation = 'contain (' + comp + ')'
        elif snippet['relation'] == 'in':
            comp = '->'.join(reversed(components))
            relation = 'contain (' + comp + ')'
        elif snippet['relation'] == 'substituted_for':
            comp = '->'.join(components)
            relation = 'substituted_for (' + comp + ')'
        elif snippet['relation'] == 'switched_to':
            comp = '->'.join(reversed(components))
            relation = 'substituted_for (' + comp + ')'
        elif snippet['relation'] == 'without':
            comp = '->'.join(components)
            relation = 'without (' + comp + ')'
        elif snippet['relation'] == 'or':
            comp = '<->'.join(components)
            relation = 'or (' + comp + ')'

        snippet['has_relation'] = relation
        del snippet['relation']


def run(snippets):
    convert2standard(snippets)