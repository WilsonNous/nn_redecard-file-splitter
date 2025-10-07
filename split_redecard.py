import os
import re
from collections import defaultdict

# ==============================
# Função principal de detecção
# ==============================
def process_file(input_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.basename(input_path).upper()

    # 1️⃣ Detecta pelo nome do arquivo
    if "EEVC" in filename:
        print("🟠 Detectado arquivo EEVC (Vendas Crédito)")
        return process_eevc(input_path, output_dir)
    elif "EEVD" in filename:
        print("🟢 Detectado arquivo EEVD (Vendas Débito)")
        return process_eevd(input_path, output_dir)
    elif "EEFI" in filename:
        print("🔵 Detectado arquivo EEFI (Financeiro)")
        return process_eefi(input_path, output_dir)

    # 2️⃣ Detecta pelo conteúdo do arquivo
    with open(input_path, "r", encoding="utf-8", errors="replace") as f:
        header = f.readline().strip()

    if header.startswith("002"):  # EEVC
        print("🟠 Detecção por conteúdo: EEVC")
        return process_eevc(input_path, output_dir)
    elif header.startswith("00"):  # EEVD (CSV)
        print("🟢 Detecção por conteúdo: EEVD")
        return process_eevd(input_path, output_dir)
    elif header.startswith("03") and header.endswith("EEFI"):
        print("🔵 Detecção por conteúdo: EEFI (posicional)")
        return process_eefi(input_path, output_dir)
    else:
        print("❌ Não foi possível determinar o tipo de arquivo.")
        return []


# ============================================
# Parser EEVC (Vendas Crédito) - layout posicional
# ============================================
def process_eevc(input_path, output_dir):
    """
    Lê um arquivo EEVC consolidado e desagrupa por estabelecimento (filiação).
    Mantém header (002) e trailer (028) para cada novo arquivo.
    Nome do arquivo final: <estab>_EEVC_<ddmmaa>_<NSA>.txt
    """
    with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
        lines = [line.rstrip('\n') for line in f]

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
        tipo = line[:3].strip()
        if tipo == "002":
            header_arquivo = line
            # NSA geralmente em 157–163 e data movimento em 143–150 (exemplo Itaú)
            nsa = line[157:163].strip() or "000"
            data_movimento = line[143:149].strip() or "000000"
        elif tipo == "028":
            trailer_arquivo = line
        elif tipo == "004":
            numero_filiacao = line[3:12].strip()
            current_estab = numero_filiacao
            grupos[current_estab].append(line)
        elif tipo == "026":
            if current_estab:
                grupos[current_estab].append(line)
                current_estab = None
        else:
            if current_estab:
                grupos[current_estab].append(line)

    gerados = []
    for estab, blocos in grupos.items():
        filename = f"{estab}_EEVC_{data_movimento}_{nsa}.txt"
        out_path = os.path.join(output_dir, filename)

        with open(out_path, 'w', encoding='utf-8') as f:
            if header_arquivo:
                f.write(header_arquivo + '\n')
            for linha in blocos:
                f.write(linha + '\n')
            if trailer_arquivo:
                f.write(trailer_arquivo + '\n')

        gerados.append(out_path)
        print(f"🧾 Gerado: {filename}")

    print(f"✅ {len(gerados)} arquivos EEVC gerados em {output_dir}.")
    return gerados


# ============================================
# Parser EEVD (Vendas Débito) - CSV delimitado
# ============================================
def process_eevd(input_path, output_dir):
    """
    Lê arquivo EEVD (CSV delimitado por vírgula) e divide por número de filiação (coluna 2).
    Nome do arquivo final: <estab>_EEVD_<ddmmaa>_<NSA>.txt
    """
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

    for i, line in enumerate(lines):
        parts = [p.strip() for p in line.split(",")]
        tipo = parts[0]
        if tipo == "00":
            header_arquivo = line
            if len(parts) > 4:
                data_movimento = parts[3].replace("/", "")[-6:] or "000000"
            if len(parts) > 6:
                nsa = parts[6].zfill(3) or "000"
        elif tipo == "04":
            trailer_arquivo = line
        elif len(parts) > 1:
            numero_filiacao = parts[1]
            grupos[numero_filiacao].append(line)

    gerados = []
    for estab, blocos in grupos.items():
        filename = f"{estab}_EEVD_{data_movimento}_{nsa}.txt"
        out_path = os.path.join(output_dir, filename)

        with open(out_path, 'w', encoding='utf-8') as f:
            if header_arquivo:
                f.write(header_arquivo)
            for linha in blocos:
                f.write(linha)
            if trailer_arquivo:
                f.write(trailer_arquivo)

        gerados.append(out_path)
        print(f"🧾 Gerado: {filename}")

    print(f"✅ {len(gerados)} arquivos EEVD gerados em {output_dir}.")
    return gerados


# ============================================
# Parser EEFI (Financeiro) - layout posicional
# ============================================
def process_eefi(input_path, output_dir):
    """
    Lê arquivo EEFI (Financeiro) e divide por estabelecimento.
    Layout posicional, tipo de registro inicia com 03 (header) e 04 (detalhes).
    Nome do arquivo final: <estab>_EEFI_<ddmmaa>_<NSA>.txt
    """
    with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
        lines = [line.rstrip('\n') for line in f]

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
            nsa = line[54:57].strip() or "000"       # estimado
            data_movimento = line[21:27].strip() or "000000"
        elif tipo == "04":
            numero_filiacao = line[2:11].strip()
            grupos[numero_filiacao].append(line)
        else:
            trailer_arquivo = line

    gerados = []
    for estab, blocos in grupos.items():
        filename = f"{estab}_EEFI_{data_movimento}_{nsa}.txt"
        out_path = os.path.join(output_dir, filename)

        with open(out_path, 'w', encoding='utf-8') as f:
            if header_arquivo:
                f.write(header_arquivo + '\n')
            for linha in blocos:
                f.write(linha + '\n')
            if trailer_arquivo:
                f.write(trailer_arquivo + '\n')

        gerados.append(out_path)
        print(f"🧾 Gerado: {filename}")

    print(f"✅ {len(gerados)} arquivos EEFI gerados em {output_dir}.")
    return gerados
