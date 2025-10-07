import os
import re
from collections import defaultdict

# ==============================
# Função principal de detecção
# ==============================
def process_file(input_path, output_dir):
    """
    Detecta o tipo de arquivo (EEVC, EEVD, EEFI) e chama o parser correto.
    """
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

    else:
        print("⚠️ Tipo de arquivo não reconhecido no nome. Tentando deduzir pelo conteúdo...")
        # fallback: tenta ler o início do arquivo
        with open(input_path, "r", encoding="utf-8", errors="replace") as f:
            header = f.readline()
        if header.startswith("002"):
            return process_eevc(input_path, output_dir)
        elif header.startswith("00"):
            return process_eevd(input_path, output_dir)
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

    for line in lines:
        tipo = line[:3].strip()  # primeiros 3 caracteres
        if tipo == "002":
            header_arquivo = line
        elif tipo == "028":
            trailer_arquivo = line
        elif tipo == "004":
            # início de um novo bloco (Header Estabelecimento)
            numero_filiacao = line[3:12].strip()
            current_estab = numero_filiacao
            grupos[current_estab].append(line)
        elif tipo == "026":
            # fim do bloco do estabelecimento
            if current_estab:
                grupos[current_estab].append(line)
                current_estab = None
        else:
            if current_estab:
                grupos[current_estab].append(line)

    # grava arquivos individuais
    gerados = []
    for estab, blocos in grupos.items():
        filename = f"EEVC_{estab}.txt"
        out_path = os.path.join(output_dir, filename)
        with open(out_path, 'w', encoding='utf-8') as f:
            if header_arquivo:
                f.write(header_arquivo + '\n')
            for linha in blocos:
                f.write(linha + '\n')
            if trailer_arquivo:
                f.write(trailer_arquivo + '\n')
        gerados.append(out_path)

    print(f"✅ {len(gerados)} arquivos EEVC gerados em {output_dir}.")
    return gerados


# ============================================
# Parser EEVD (Vendas Débito) - CSV delimitado
# ============================================
def process_eevd(input_path, output_dir):
    """
    Lê arquivo EEVD (CSV delimitado por vírgula) e divide por número de filiação (coluna 2).
    """
    with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()

    if not lines:
        print("Arquivo vazio.")
        return []

    header_arquivo = None
    trailer_arquivo = None
    grupos = defaultdict(list)

    for i, line in enumerate(lines):
        parts = [p.strip() for p in line.split(",")]
        tipo = parts[0]
        if tipo == "00":
            header_arquivo = line
        elif tipo == "04":
            trailer_arquivo = line
        elif tipo == "01":
            # registro de resumo por PV
            numero_filiacao = parts[1]
            grupos[numero_filiacao].append(line)
        else:
            # adiciona registros do mesmo PV
            if len(parts) > 1:
                numero_filiacao = parts[1]
                grupos[numero_filiacao].append(line)

    gerados = []
    for estab, blocos in grupos.items():
        filename = f"EEVD_{estab}.txt"
        out_path = os.path.join(output_dir, filename)
        with open(out_path, 'w', encoding='utf-8') as f:
            if header_arquivo:
                f.write(header_arquivo)
            for linha in blocos:
                f.write(linha)
            if trailer_arquivo:
                f.write(trailer_arquivo)
        gerados.append(out_path)

    print(f"✅ {len(gerados)} arquivos EEVD gerados em {output_dir}.")
    return gerados


# ============================================
# Parser EEFI (Financeiro) - estrutura semelhante ao EEVD
# ============================================
def process_eefi(input_path, output_dir):
    """
    Divide o arquivo EEFI por número de filiação (coluna 2, CSV).
    """
    with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()

    if not lines:
        print("Arquivo vazio.")
        return []

    header_arquivo = None
    trailer_arquivo = None
    grupos = defaultdict(list)

    for i, line in enumerate(lines):
        parts = [p.strip() for p in line.split(",")]
        tipo = parts[0]
        if tipo == "00":
            header_arquivo = line
        elif tipo == "04":
            trailer_arquivo = line
        elif len(parts) > 1:
            numero_filiacao = parts[1]
            grupos[numero_filiacao].append(line)

    gerados = []
    for estab, blocos in grupos.items():
        filename = f"EEFI_{estab}.txt"
        out_path = os.path.join(output_dir, filename)
        with open(out_path, 'w', encoding='utf-8') as f:
            if header_arquivo:
                f.write(header_arquivo)
            for linha in blocos:
                f.write(linha)
            if trailer_arquivo:
                f.write(trailer_arquivo)
        gerados.append(out_path)

    print(f"✅ {len(gerados)} arquivos EEFI gerados em {output_dir}.")
    return gerados
