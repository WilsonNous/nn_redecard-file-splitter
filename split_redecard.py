import os
import re
from collections import defaultdict

def process_file(input_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()

    # agrupa linhas por CNPJ (14 dígitos)
    groups = defaultdict(list)
    cnpj_re = re.compile(r'\b(\d{14})\b')

    for line in lines:
        match = cnpj_re.search(line)
        if match:
            cnpj = match.group(1)
            groups[cnpj].append(line)
        else:
            groups['SEM_CNPJ'].append(line)

    generated = []
    for cnpj, group_lines in groups.items():
        filename = f"{os.path.splitext(os.path.basename(input_path))[0]}_{cnpj}.txt"
        out_path = os.path.join(output_dir, filename)
        with open(out_path, 'w', encoding='utf-8') as out:
            out.writelines(group_lines)
        generated.append(out_path)

    return generated
