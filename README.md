# VIBRA — Rede Social (Protótipo)

Bem-vindo! Este repositório tem um site básico da VIBRA (Flask + SQLite) feito para **testes**.  
Você consegue **logar**, **postar no feed**, e entrar num **painel admin**.

---

## 1) Como baixar e abrir o projeto
1. Clique em **Code → Download ZIP** (ou use o ZIP que recebi de você).
2. Extraia o ZIP numa pasta no seu computador (ex.: `C:\Users\seu_usuário\VIBRA` ou `~/VIBRA`).

Estrutura principal:
```
/
├─ vibra_site/              # Código da aplicação
│  ├─ app.py
│  ├─ config.py
│  ├─ requirements.txt
│  ├─ templates/            # HTML (Jinja2)
│  ├─ static/               # CSS/arquivos estáticos
│  └─ vibra.db              # (gerado na primeira execução)
├─ Dockerfile               # Para deploy com Docker
├─ .dockerignore
├─ render.yaml              # Para deploy no Render.com
├─ Procfile                 # Para plataformas herokuish / Railway
├─ runtime.txt              # Versão do Python (herokuish)
├─ .gitignore
└─ LICENSE
```

---

## 2) Como rodar localmente (sem Docker)
Requisitos: **Python 3.10+**
```bash
cd vibra_site
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows
# .venv\Scripts\activate

pip install -r requirements.txt
python app.py
```
Acesse no navegador: **http://localhost:5000**

**Logins de teste:**
- Admin: `admin@vibra.com` / `vibra123`
- Demo:  `demo@vibra.com`  / `vibra123`

> O banco `vibra.db` será criado automaticamente e os usuários seeds inseridos na primeira execução.

---

## 3) Como criar uma conta no GitHub e subir o repositório (passo a passo)
### Opção simples (pelo site)
1. Acesse **https://github.com** e crie sua conta (se ainda não tiver).
2. Clique no canto superior direito em **+ → New repository**.
3. Nomeie o repositório, ex.: **vibra**. Deixe como **Public** (pode ser Private também).
4. NÃO marque a opção de criar README/ .gitignore pelo site (como já temos no ZIP).
5. Clique **Create repository**.
6. Na página do repositório, clique em **uploading an existing file**.
7. Arraste e solte TODA a pasta do repositório (os arquivos do ZIP extraídos).  
   - Importante: suba **tudo** que está dentro da pasta principal (inclusive `vibra_site/`, `Dockerfile`, `render.yaml`, etc.).
8. Desça a página e clique em **Commit changes**.

### Opção via linha de comando (Git)
1. Instale o Git: https://git-scm.com/downloads
2. No GitHub, crie o repositório (passos 2–5 acima).
3. No **Terminal / Prompt**:
```bash
cd /caminho/da/pasta/que/você/extraiu
git init
git add .
git commit -m "VIBRA: primeira versão"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/SEU_REPO.git
git push -u origin main
```
Troque `SEU_USUARIO/SEU_REPO` pelo seu usuário e nome do repositório.

---

## 4) Colocando online (Render.com — mais fácil)
> Esta opção NÃO usa Docker e cria um **disco persistente** para o SQLite.

1. Crie conta em https://render.com e conecte seu GitHub.
2. Certifique-se que o arquivo **`render.yaml`** está na raiz do seu repositório.
3. No Render: **New → Blueprint** e selecione o seu repo.
4. Aceite as configurações padrão e clique em **Apply** para iniciar o deploy.
5. Quando finalizar, acesse a URL pública que o Render mostrar.

**O blueprint já faz:**
- Instala dependências (`requirements.txt`), inicia com `gunicorn`.
- Cria um disco em `/opt/render/project/src/data` e define `DATABASE=/opt/render/project/src/data/vibra.db`.
- Gera `SECRET_KEY` automaticamente.

Se quiser configurar manualmente: no serviço Web do Render, vá em **Environment** e ajuste/adicione:
- `SECRET_KEY` (texto aleatório e longo)
- `DATABASE=/opt/render/project/src/data/vibra.db`

---

## 5) Colocando online (Railway — com Docker)
1. Certifique-se de que o repo tem `Dockerfile` e `.dockerignore` na raiz.
2. Em https://railway.app → **New Project → Deploy from GitHub**.
3. Em **Variables**, defina:
   - `PORT=8080`
   - `SECRET_KEY=uma_chave_bem_secreta`
   - `DATABASE=/app/data/vibra.db`
4. Em **Volumes**, crie um volume e monte em `/app/data` (para persistência).
5. Deploy e pronto. A URL pública aparece no painel.

---

## 6) Dicas e personalizações
- **Mudar senha do admin:** entre no **/admin/users** e crie um novo admin; depois remova o padrão do banco, se quiser.
- **Trocar tema/cores:** edite `vibra_site/static/styles.css`.
- **Novas páginas ou campos:** edite os HTML em `vibra_site/templates/` e o Python em `vibra_site/app.py`.
- **Banco Postgres (produção):** recomendo migrar para Postgres nas plataformas. Posso adaptar o código com SQLAlchemy se você quiser.

---

## 7) Suporte
Se travar em qualquer passo, me diga **em qual etapa parou** (ex.: “erro ao dar push no Git”, “deploy falhou no Render”) que eu te guio com o comando certo 🙂
