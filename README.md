# 🧩 REDECARD Splitter (EEVC / EEVD / EEFI)

Aplicação **Flask + Python** para automatizar a **desagregação de arquivos da REDE**  
(EEVC, EEVD, EEFI) por **estabelecimento (número de filiação / PV)**.

Permite o **upload de múltiplos arquivos simultaneamente**, processa e gera  
**um pacote `.zip` com todos os resultados individuais**, mantendo a estrutura  
de header e trailer de cada arquivo original.

---

## 🚀 Como funciona

1. Faça upload de um ou mais arquivos originais (EEVC, EEVD, EEFI);
2. A aplicação identifica automaticamente o tipo de arquivo:
   - 🟠 **EEVC** → Vendas Crédito (layout posicional)
   - 🟢 **EEVD** → Vendas Débito (CSV)
   - 🔵 **EEFI** → Financeiro (posicional)
3. Cada arquivo é desmembrado por **estabelecimento (filiação/PV)**;
4. Um novo arquivo é gerado para cada PV com nome padronizado e dados do header;
5. Todos os arquivos processados são empacotados em um `.zip` e disponibilizados para download.

---

## 💡 Principais recursos

- ✅ Processamento **automático por tipo de layout**  
- ✅ Suporte a **EEVC, EEVD e EEFI**  
- ✅ Upload múltiplo e download consolidado (.zip)  
- ✅ Nome inteligente de saída (inclui PV, data e NSA)  
- ✅ Compatível com o **Render (Free Tier)**  
- ✅ Configuração de layout em `config_rede.json`  
- ✅ Código modular, escalável e documentado  

---

## 🧱 Estrutura de diretórios

```
redecard-splitter/
│
├── app.py                 ← Interface Flask + geração de ZIP
├── split_redecard.py      ← Motor de parsing e split (EEVC / EEVD / EEFI)
├── config_rede.json       ← Configuração de layouts e parâmetros gerais
├── templates/
│   └── index.html         ← Interface de upload
├── static/
│   └── style.css          ← (opcional)
├── requirements.txt       ← Dependências Python
└── README.md              ← Este arquivo
```

---

## ⚙️ Instalação local (opcional)

```bash
git clone https://github.com/<seu-usuario>/redecard-splitter.git
cd redecard-splitter
pip install -r requirements.txt
python app.py
```

Acesse em: [http://localhost:5000](http://localhost:5000)

---

## 🌐 Deploy automático no Render

**Build Command:** `pip install -r requirements.txt`  
**Start Command:** `gunicorn app:app`  
**Runtime:** Python 3  
**Plan:** Free  

Após o build, a aplicação estará disponível em:
```
https://redecard-splitter.onrender.com
```

---

## 🗺️ TOPOLOGIA DO PROJETO

```
[USUÁRIO] → [INTERFACE WEB (Flask + HTML)]  
  ↓  
📂 uploads/ (armazenamento temporário)  
  ↓  
🧠 split_redecard.py (motor de parsing e desagregação)  
  ↳ Detecta tipo: EEVC / EEVD / EEFI  
  ↳ Lê header, trailer e blocos por PV  
  ↳ Gera arquivos individuais por estabelecimento  
  ↓  
📂 outputs/ (arquivos processados)  
  ↓  
🧳 app.py → empacota resultados em ZIP  
  ↓  
⬇️ Usuário baixa `resultados_rede_splitter.zip`
```

---

## 📁 Padrão de Nomenclatura de Saída

Cada arquivo gerado segue o formato:

```
<estabelecimento>_<TIPO>_<ddmmaa>_<NSA>.txt
```

| Campo | Origem | Exemplo | Descrição |
|--------|---------|----------|------------|
| **estabelecimento** | Header ou detalhe | `010034671` | Número de filiação (PV) |
| **TIPO** | Tipo do layout | `EEVC`, `EEVD`, `EEFI` | Identificação do tipo de arquivo |
| **ddmmaa** | Header (data do movimento) | `071025` | Data de geração do movimento |
| **NSA** | Header | `001` | Número Sequencial do Arquivo |

📄 **Exemplo real de saída:**
```
010034671_EEFI_071025_001.txt
010045778_EEVC_071025_002.txt
009887654_EEVD_071025_001.txt
```

---

## ⚙️ Configuração dos Layouts (`config_rede.json`)

```json
{
  "EEVC": { "formato": "posicional", "header_arquivo": "002", "trailer_arquivo": "028" },
  "EEVD": { "formato": "csv", "delimiter": ",", "header_arquivo": "00", "trailer_arquivo": "04" },
  "EEFI": { "formato": "posicional", "header_arquivo": "03", "trailer_arquivo": "09" }
}
```

---

## 🧳 Saída esperada

Após o processamento, será gerado um arquivo ZIP contendo todos os arquivos desmembrados:

```
010034671_EEFI_071025_001.txt
010045678_EEVC_071025_001.txt
009887654_EEVD_071025_002.txt
...
```

Cada arquivo contém:
- Header do arquivo  
- Header do estabelecimento  
- Registros de detalhe  
- Trailer do estabelecimento  
- Trailer do arquivo  

---

## 🔍 Próximas evoluções

- 📈 Recalcular totais no trailer (opcional)
- 🧾 Geração de logs por execução
- 💾 Integração com banco de dados MySQL (auditoria)
- 🧠 Interface de status em tempo real
- ⚡ Upload direto via API REST (sem interface web)

---

## ✉️ Contato / Suporte

**Autor:** Wilson Martins  
**Organização:** Netunna Software  
**E-mail:** wilson.martins@netunna.com.br  
**Propósito:** Automação de EDI e conciliação financeira para adquirentes e bancos.  


