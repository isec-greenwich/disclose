from __future__ import division
from stix2 import FileSystemSource, Filter
import csv


def get_all_techniques(src):
    fl = [
        Filter('type', '=', 'attack-pattern'),
        Filter('x_mitre_platforms', 'contains', 'Windows')
    ]  # add only windows query
    techniques = src.query(fl)
    return techniques


def get_relations_for_techniques(src, technique):
    # get id for technique
    t_id = technique.id

    # get relationships for technique
    fl = [
        Filter('type', '=', 'relationship'),
        Filter('relationship_type', '=', 'uses'),
        Filter('target_ref', '=', t_id)
    ]
    relations = src.query(fl)
    return relations


def get_references_for_techniques(relations):
    # get all reports from relations
    reports = []
    for i in relations:
        try:
            for j in i.external_references:
                reports.append(j.url)
        except:
            pass
    return reports


fs = FileSystemSource('/home/zen/cti/enterprise-attack')
techniques = get_all_techniques(fs)
tech_reports = {}
T = {}
for i in techniques:
    tech_reports[i.name] = get_relations_for_techniques(fs, i)

# do some filtering
temp = {}
for i in tech_reports:
    if len(tech_reports[i]) > 0:
        temp[i] = tech_reports[i]

# get the references from the relationships
tech_reports = {}
for i in temp:
    tech_reports[i] = list(set(get_references_for_techniques(temp[i])))

del temp

for i in tech_reports:
    temp = {'TTPs': i}
    for j in tech_reports:
        temp[j] = round(len(list(set(tech_reports[i]) & set(tech_reports[j]))) / len(tech_reports[i]), 2)
    T[i] = temp

# write results to csv
with open('ttp_relationships.csv', 'w') as csv_file:
    csv_columns = ['TTPs', 'Spearphishing Attachment', 'Spearphishing Link', 'Drive-by Compromise', 'User Execution',
                   'Scripting', 'PowerShell', 'Process Injection', 'New Service', 'Registry Run Keys / Startup Folder',
                   'Network Share Discovery', 'System Service Discovery', 'System Network Configuration Discovery',
                   'Credential Dumping', 'Standard Application Layer Protocol', 'Custom Command and Control Protocol',
                   'Exfiltration Over Command and Control Channel', 'Exfiltration Over Alternative Protocol',
                   'Data from Network Shared Drive', 'Data from Local System', 'Pass the Hash'
                   ]
    writer = csv.DictWriter(csv_file, fieldnames=csv_columns)
    writer.writeheader()
    for i in T:
        writer.writerow(T[i])
