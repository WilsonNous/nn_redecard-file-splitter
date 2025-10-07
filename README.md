# REDECARD Splitter (EEVC / EEVD / EEFI)

Aplicação Flask para dividir arquivos da REDE (EEVC, EEVD, EEFI) por estabelecimento.

## 🚀 Como funciona

1. Envie o arquivo original (agrupado pela matriz)
2. A aplicação divide automaticamente por CNPJ de estabelecimento
3. São gerados novos arquivos com o header e trailer correspondentes

## 🌐 Deploy automático

Hospedado no Render:  
- Build: `pip install -r requirements.txt`
- Start: `gunicorn app:app`

