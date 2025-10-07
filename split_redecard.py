import os
import re
from collections import defaultdict
from datetime import datetime

# =============== utilidades ===============

INVALID_FN_CHARS = re.compile(r'[^A-Za-z0-9._-]')

def sanitize_filename(name: str) -> str:
    """Remove caracteres inválidos para nome de arquivo."""
    s = INVALID_FN_CHARS.sub('_', name.strip())
    return re.sub(r'_+', '_', s)

def ensure_outfile(path_dir: str, filename: str) -> str:
    os.makedirs(path_dir, exist_ok=True)
    filename = sanitize_filename(filename)
    return os.path.join(path_dir, filename)

def safe_slice(s: str, start: int, end: int) -> str:
    """Slice seguro para strings."""
    return s[start:end] if len(s) >= end else s[start:]

# =============== detecção ===============

def process_file(input_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.basename(input_path).upper()

    if "EEVC" in filename:
        print("🟠 Detectado arquivo EEVC (Vendas Crédito)")
        return process_eevc(input_path, output_dir)
    elif "EEVD" in filename:
        print("🟢 Detectado arquivo EEVD (Vendas Débito)")
        return process_eevd(input_path, output_dir)
    elif "EEFI" in filename:
        print("🔵 Detectado arquivo EEFI (Financeiro)")
        return process_eefi(input_path, output_dir)

    with open(input_path, "r", encoding="utf-8", errors="replace") as f:
        header = f.readline().strip()

    if header.startswith("002"):
        return process_eevc(input_path, output_dir)
    elif header.startswith("00"):
        return process_eevd(input_path, output_dir)
    elif header.startswith("03"):
        return process_eefi(input_path, output_dir)
    else:
        print("❌ Tipo de arquivo desconhecido.")
        return []

# =============== EEVC (Crédito) ===============

def process_eevc(input_path, output_dir):
    with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
        lines = [l.rstrip('\n') for l in f]

    if not lines:
        print("Arquivo vazio.")
        return []

    header_arquivo = None
    trailer_arquivo = None
    grupos = defaultdict(list)
    current_estab = None
    data_movimento = "000000"
    nsa = "000"

    for line in lines:
        tipo = line[:3]
        if tipo == "002":
            header_arquivo = line
            data_movimento = safe_slice(line, 143, 151).strip()
            if re.fullmatch(r'\d{8}', data_movimento):
                data_movimento = data_movimento[:4] + data_movimento[-2:]
            else:
                data_movimento = "000000"
            nsa_raw = safe_slice(line, 157, 163).strip()
            nsa = nsa_raw[-3:] if nsa_raw.isdigit() else "000"
        elif tipo == "004":
            pv = safe_slice(line, 3, 12).strip()
            current_estab = pv
            grupos[pv].append(line)
        elif tipo == "026":
            if current_estab:
                grupos[current_estab].append(line)
                current_estab = None
        elif tipo == "028":
            trailer_arquivo = line
        else:
            if current_estab:
                grupos[current_estab].append(line)

    gerados = []
    for estab, blocos in grupos.items():
        nome = f"{estab}_EEVC_{data_movimento}_{nsa}.txt"
        out_path = ensure_outfile(output_dir, nome)
        with open(out_path, 'w', encoding='utf-8') as f:
            if header_arquivo:
                f.write(header_arquivo + '\n')
            f.writelines([b + '\n' for b in blocos])
            if trailer_arquivo:
                f.write(trailer_arquivo + '\n')
        gerados.append(out_path)
        print(f"🧾 Gerado: {os.path.basename(out_path)}")

    print(f"✅ {len(gerados)} arquivos EEVC gerados.")
    return gerados

# =============== EEVD (Débito) ===============

def process_eevd(input_path, output_dir):
    with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()

    if not lines:
        print("Arquivo vazio.")
        return []

    header_arquivo = None
    trailer_arquivo = None
    grupos = defaultdict(list)
    data_movimento = "000000"
    nsa = "000"

    for line in lines:
        parts = [p.strip() for p in line.split(",")]
        tipo = parts[0]
        if tipo == "00":
            header_arquivo = line
            if len(parts) > 3 and re.fullmatch(r'\d{8}', parts[3]):
                d = parts[3]
                data_movimento = d[:4] + d[-2:]
            if len(parts) > 7 and parts[7].isdigit():
                nsa = parts[7][-3:]
        elif tipo == "04":
            trailer_arquivo = line
        elif len(parts) > 1:
            pv = parts[1]
            grupos[pv].append(line)

    gerados = []
    for estab, blocos in grupos.items():
        nome = f"{estab}_EEVD_{data_movimento}_{nsa}.txt"
        out_path = ensure_outfile(output_dir, nome)
        with open(out_path, 'w', encoding='utf-8') as f:
            if header_arquivo:
                f.write(header_arquivo)
            f.writelines(blocos)
            if trailer_arquivo:
                f.write(trailer_arquivo)
        gerados.append(out_path)
        print(f"🧾 Gerado: {os.path.basename(out_path)}")

    print(f"✅ {len(gerados)} arquivos EEVD gerados.")
    return gerados

# =============== EEFI (Financeiro) ===============

def process_eefi(input_path, output_dir):
    with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
        lines = [l.rstrip('\n') for l in f]

    if not lines:
        print("Arquivo vazio.")
        return []

    header_arquivo = None
    trailer_arquivo = None
    grupos = defaultdict(list)
    data_movimento = "000000"
    nsa = "000"

    for line in lines:
        tipo = line[:2]
        if tipo == "03":
            header_arquivo = line
            d = safe_slice(line, 21, 29).strip()
            if re.fullmatch(r'\d{8}', d):
                data_movimento = d[:4] + d[-2:]
            nsa_raw = safe_slice(line, 54, 60).strip()
            nsa = nsa_raw[-3:] if nsa_raw.isdigit() else "000"
        elif tipo == "04":
            pv = safe_slice(line, 2, 11).strip()
            grupos[pv].append(line)
        else:
            trailer_arquivo = line

    gerados = []
    for estab, blocos in grupos.items():
        nome = f"{estab}_EEFI_{data_movimento}_{nsa}.txt"
        out_path = ensure_outfile(output_dir, nome)
        with open(out_path, 'w', encoding='utf-8') as f:
            if header_arquivo:
                f.write(header_arquivo + '\n')
            f.writelines([b + '\n' for b in blocos])
            if trailer_arquivo:
                f.write(trailer_arquivo + '\n')
        gerados.append(out_path)
        print(f"🧾 Gerado: {os.path.basename(out_path)}")

    print(f"✅ {len(gerados)} arquivos EEFI gerados.")
    return gerados
