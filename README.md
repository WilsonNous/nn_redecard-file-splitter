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
   - 🔵 **EEFI** → Financeiro (CSV)
3. Cada arquivo é desmembrado por **estabelecimento (filiação/PV)**;
4. Um novo arquivo é gerado para cada PV, contendo:
   - Header do arquivo (002 ou 00)
   - Header do estabelecimento
   - Registros de detalhe
   - Trailer do estabelecimento
   - Trailer do arquivo
5. Todos os arquivos processados são empacotados em um `.zip` e disponibilizados para download.

---

## 💡 Principais recursos

- ✅ Processamento **automático por tipo de layout**  
- ✅ Suporte a **EEVC, EEVD e EEFI**  
- ✅ Upload múltiplo  
- ✅ Geração de **ZIP consolidado**  
- ✅ Compatível com o **Render (Free Tier)**  
- ✅ Configuração de layout em `config_rede.json`  
- ✅ Código modular e escalável  

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

A aplicação está pronta para deploy direto no Render.

**Configuração:**

- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `gunicorn app:app`
- **Runtime:** Python 3
- **Region:** Oregon (recomendada)
- **Plan:** Free

**Passos:**
1. Acesse [https://render.com](https://render.com)
2. Crie um novo Web Service e conecte seu GitHub
3. Escolha o repositório `redecard-splitter`
4. Configure os comandos acima e clique em **Deploy**

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

### 🔧 Componentes

| Componente | Função |
|-------------|--------|
| **Flask App (`app.py`)** | Interface web, upload e geração de ZIP |
| **Motor de Split (`split_redecard.py`)** | Processamento dos arquivos e separação por PV |
| **Configuração (`config_rede.json`)** | Define layouts e comportamento de parsing |
| **Templates HTML** | Interface de upload amigável |
| **Render Hosting** | Deploy em nuvem com CI/CD automático |

---

## ⚙️ Configuração dos Layouts (`config_rede.json`)

O arquivo `config_rede.json` define as regras de cada layout:

```json
{
  "EEVC": { "formato": "posicional", "header_arquivo": "002", "trailer_arquivo": "028" },
  "EEVD": { "formato": "csv", "delimiter": ",", "header_arquivo": "00", "trailer_arquivo": "04" },
  "EEFI": { "formato": "csv", "delimiter": ",", "header_arquivo": "00", "trailer_arquivo": "04" }
}
```

---

## 🧳 Saída esperada

Após o processamento, será gerado um arquivo ZIP contendo:
```
EEVC_123456789.txt
EEVC_987654321.txt
EEVD_123456789.txt
EEFI_123456789.txt
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
**E-mail:** contato@netunna.com.br  
**Propósito:** Automação de EDI e conciliação financeira para adquirentes e bancos.  

