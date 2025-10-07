import os
import re
from collections import defaultdict, Counter
from datetime import datetime

# =============== utilidades comuns ===============

INVALID_FN_CHARS = re.compile(r'[^A-Za-z0-9._-]')

def sanitize_filename(name: str) -> str:
    """Remove caracteres inválidos para nome de arquivo e colapsa múltiplos underscores."""
    s = INVALID_FN_CHARS.sub('_', name.strip())
    s = re.sub(r'_+', '_', s)
    return s

def safe_slice(s: str, start: int, end: int) -> str:
    """Slice tolerante (start/end 0-based, end exclusivo)."""
    if s is None:
        return ""
    n = len(s)
    start = max(0, start)
    end = max(0, end)
    if start >= n:
        return ""
    return s[start:min(end, n)]

def pick_ddmmaa_from_dates(dates_ddmmyyyy: list[str]) -> str:
    """
    Recebe uma lista de datas no formato ddmmyyyy e devolve ddmmaa:
    - pega a data mais frequente; em empate, a mais recente.
    """
    if not dates_ddmmyyyy:
        return "000000"
    freq = Counter(dates_ddmmyyyy)
    # ordena por frequência e depois por data (mais recente)
    best = sorted(freq.items(), key=lambda kv: (kv[1], datetime.strptime(kv[0], "%d%m%Y")), reverse=True)[0][0]
    return best[:4] + best[-2:]  # ddmm + aa

DATE_PATTERNS = [
    re.compile(r'(?<!\d)(\d{2})(\d{2})(\d{4})(?!\d)'),        # ddmmyyyy
    re.compile(r'(?<!\d)(\d{2})/(\d{2})/(\d{2,4})(?!\d)'),    # dd/mm/aa|yyyy
]

def scan_dates_ddmmyyyy(lines: list[str]) -> list[str]:
    """Varre linhas e extrai todas as datas convertidas para ddmmyyyy."""
    found = []
    for ln in lines:
        for pat in DATE_PATTERNS:
            for m in pat.finditer(ln):
                dd, mm, yy = m.group(1), m.group(2), m.group(3)
                if len(yy) == 2:
                    # assume 20xx para anos de 00..69 e 19xx para 70..99? Simples: 20xx direto
                    yy = "20" + yy
                # valida básica
                try:
                    datetime.strptime(dd+mm+yy, "%d%m%Y")
                except ValueError:
                    continue
                found.append(dd+mm+yy)
    return found

def ensure_outfile(path_dir: str, filename: str) -> str:
    os.makedirs(path_dir, exist_ok=True)
    filename = sanitize_filename(filename)
    return os.path.join(path_dir, filename)

# =============== detecção de tipo ===============

def process_file(input_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.basename(input_path).upper()

    # 1) por nome
    if "EEVC" in filename:
        print("🟠 Detectado arquivo EEVC (Vendas Crédito)")
        return process_eevc(input_path, output_dir)
    if "EEVD" in filename:
        print("🟢 Detectado arquivo EEVD (Vendas Débito)")
        return process_eevd(input_path, output_dir)
    if "EEFI" in filename:
        print("🔵 Detectado arquivo EEFI (Financeiro)")
        return process_eefi(input_path, output_dir)

    # 2) por conteúdo
    with open(input_path, "r", encoding="utf-8", errors="replace") as f:
        header = f.readline().rstrip("\n")

    if header.startswith("002"):
        print("🟠 Detecção por conteúdo: EEVC")
        return process_eevc(input_path, output_dir)
    elif header.startswith("00"):  # csv-like
        print("🟢 Detecção por conteúdo: EEVD")
        return process_eevd(input_path, output_dir)
    elif header.startswith("03") and header.endswith("EEFI"):
        print("🔵 Detecção por conteúdo: EEFI (posicional)")
        return process_eefi(input_path, output_dir)

    print("❌ Não foi possível determinar o tipo de arquivo.")
    return []

# =============== EEVC (posicional) ===============

def process_eevc(input_path, output_dir):
    """
    EEVC: posicional.
    Blocos: 002 header_arquivo | 004 header_estab | ... | 026 trailer_estab | 028 trailer_arquivo
    Nome: <estab>_EEVC_<ddmmaa>_<NSA>.txt
    """
    with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
        lines = [ln.rstrip('\n') for ln in f]

    if not lines:
        print("Arquivo vazio.")
        return []

    header_arquivo = None
    trailer_arquivo = None
    grupos = defaultdict(list)
    current_estab = None
    nsa = "000"
    ddmmaa = "000000"

    # para fallback de data, coletamos todas as datas
    all_dates = []

    for line in lines:
        # coleta datas p/ fallback
        all_dates.extend(scan_dates_ddmmyyyy([line]))

        tipo = line[:3].strip()
        if tipo == "002":
            header_arquivo = line
            # 🔧 Ajuste pelo layout se souber as posições:
            # Exemplo (estimado): NSA em [157:163], data ddmmyy a partir de [143:149]
            nsa_try = safe_slice(line, 157, 163).strip()
            # se NSA vier com 6 e for numérico, usa os 3 últimos; se vier com 3, mantém
            if nsa_try.isdigit():
                nsa = nsa_try[-3:].zfill(3)
            # data: se tiver ddmmyy direto:
            dm_try = safe_slice(line, 143, 149).strip()
            if re.fullmatch(r'\d{6}', dm_try):
                ddmmaa = dm_try
        elif tipo == "028":
            trailer_arquivo = line
        elif tipo == "004":
            pv = safe_slice(line, 3, 12).strip()
            current_estab = pv or "000000000"
            grupos[current_estab].append(line)
        elif tipo == "026":
            if current_estab:
                grupos[current_estab].append(line)
                current_estab = None
        else:
            if current_estab:
                grupos[current_estab].append(line)

    # fallback de data para ddmmaa (pega data mais frequente -> mais recente)
    if ddmmaa == "000000":
        ddmmaa = pick_ddmmaa_from_dates(all_dates)

    gerados = []
    for estab, blocos in grupos.items():
        out_name = f"{estab}_EEVC_{ddmmaa}_{nsa}.txt"
        out_path = ensure_outfile(output_dir, out_name)
        with open(out_path, 'w', encoding='utf-8') as f:
            if header_arquivo:
                f.write(header_arquivo + '\n')
            for linha in blocos:
                f.write(linha + '\n')
            if trailer_arquivo:
                f.write(trailer_arquivo + '\n')
        gerados.append(out_path)
        print(f"🧾 Gerado: {os.path.basename(out_path)}")

    print(f"✅ {len(gerados)} arquivos EEVC gerados em {output_dir}.")
    return gerados

# =============== EEVD (CSV) ===============

def process_eevd(input_path, output_dir):
    """
    EEVD: CSV (vírgula).
    Nome: <estab>_EEVD_<ddmmaa>_<NSA>.txt

    Observação: as posições/colunas variam por versão.
    - Ajuste aqui as colunas se tiver do PDF.
      Ex.: header "00,...,DATA,...,NSA"
    """
    with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()

    if not lines:
        print("Arquivo vazio.")
        return []

    header_arquivo = None
    trailer_arquivo = None
    grupos = defaultdict(list)
    nsa = "000"
    ddmmaa = "000000"

    all_dates = []

    for idx, line in enumerate(lines):
        parts = [p.strip() for p in line.rstrip("\n").split(",")]
        if not parts:
            continue
        tipo = parts[0]

        # coleta datas p/ fallback
        all_dates.extend(scan_dates_ddmmyyyy([line]))

        if tipo == "00":
            header_arquivo = line
            # 🔧 Ajuste colunas pelo seu layout EEVD:
            # exemplo: data do movimento em parts[3], NSA em parts[6]
            if len(parts) > 3:
                dm_raw = parts[3]
                # aceita dd/mm/aa|yyyy ou ddmmyyyy
                m = re.search(r'(\d{2})/(\d{2})/(\d{2,4})|(\d{2})(\d{2})(\d{4})', dm_raw)
                if m:
                    if m.group(1):  # dd/mm/aa|yyyy
                        dd, mm, yy = m.group(1), m.group(2), m.group(3)
                        if len(yy) == 2:
                            yy = "20" + yy
                        try:
                            datetime.strptime(dd+mm+yy, "%d%m%Y")
                            ddmmaa = dd + mm + yy[-2:]
                        except ValueError:
                            pass
                    else:  # ddmmyyyy
                        dd, mm, yy = m.group(4), m.group(5), m.group(6)
                        try:
                            datetime.strptime(dd+mm+yy, "%d%m%Y")
                            ddmmaa = dd + mm + yy[-2:]
                        except ValueError:
                            pass
            if len(parts) > 6:
                nsa_raw = parts[6]
                if re.fullmatch(r'\d{1,6}', nsa_raw):
                    nsa = nsa_raw[-3:].zfill(3)

        elif tipo == "04":
            trailer_arquivo = line
        else:
            # assumimos PV em parts[1] (ajuste se necessário)
            pv = parts[1] if len(parts) > 1 else "000000000"
            grupos[pv].append(line)

    # fallbacks
    if ddmmaa == "000000":
        ddmmaa = pick_ddmmaa_from_dates(all_dates)

    gerados = []
    for estab, blocos in grupos.items():
        out_name = f"{estab}_EEVD_{ddmmaa}_{nsa}.txt"
        out_path = ensure_outfile(output_dir, out_name)
        with open(out_path, 'w', encoding='utf-8') as f:
            if header_arquivo:
                f.write(header_arquivo)
            for linha in blocos:
                f.write(linha)
            if trailer_arquivo:
                f.write(trailer_arquivo)
        gerados.append(out_path)
        print(f"🧾 Gerado: {os.path.basename(out_path)}")

    print(f"✅ {len(gerados)} arquivos EEVD gerados em {output_dir}.")
    return gerados

# =============== EEFI (posicional) ===============

def process_eefi(input_path, output_dir):
    """
    EEFI: posicional.
    Header 03..., Detalhe 04..., (Trailer pode variar).
    Nome: <estab>_EEFI_<ddmmaa>_<NSA>.txt
    """
    with open(input_path, 'r', encoding='utf-8', errors='replace') as f:
        lines = [ln.rstrip('\n') for ln in f]

    if not lines:
        print("Arquivo vazio.")
        return []

    header_arquivo = None
    trailer_arquivo = None
    grupos = defaultdict(list)
    nsa = "000"
    ddmmaa = "000000"

    all_dates = []

    for line in lines:
        all_dates.extend(scan_dates_ddmmyyyy([line]))

        tipo = line[:2]
        if tipo == "03":
            header_arquivo = line
            # 🔧 Ajuste pelo layout do seu PDF:
            # Exemplo (com base no seu trecho): data [21:27] como ddmmaa, NSA [54:57]
            dm_try = safe_slice(line, 21, 27).strip()
            if re.fullmatch(r'\d{6}', dm_try):
                ddmmaa = dm_try
            nsa_try = safe_slice(line, 54, 57).strip()
            if nsa_try.isdigit():
                nsa = nsa_try[-3:].zfill(3)
        elif tipo == "04":
            # PV em [2:11] pelo teu exemplo
            pv = safe_slice(line, 2, 11).strip() or "000000000"
            grupos[pv].append(line)
        else:
            trailer_arquivo = line

    if ddmmaa == "000000":
        ddmmaa = pick_ddmmaa_from_dates(all_dates)

    gerados = []
    for estab, blocos in grupos.items():
        out_name = f"{estab}_EEFI_{ddmmaa}_{nsa}.txt"
        out_path = ensure_outfile(output_dir, out_name)
        with open(out_path, 'w', encoding='utf-8') as f:
            if header_arquivo:
                f.write(header_arquivo + '\n')
            for linha in blocos:
                f.write(linha + '\n')
            if trailer_arquivo:
                f.write(trailer_arquivo + '\n')
        gerados.append(out_path)
        print(f"🧾 Gerado: {os.path.basename(out_path)}")

    print(f"✅ {len(gerados)} arquivos EEFI gerados em {output_dir}.")
    return gerados
