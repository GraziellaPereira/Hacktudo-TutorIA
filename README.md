# 🎓 TutorIA

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python">
  <img src="https://img.shields.io/badge/FastAPI-API-green?style=for-the-badge&logo=fastapi">
  <img src="https://img.shields.io/badge/Next.js-Frontend-black?style=for-the-badge&logo=next.js">
  <img src="https://img.shields.io/badge/SQLite-Database-blue?style=for-the-badge&logo=sqlite">
  <img src="https://img.shields.io/badge/Gemini-AI-orange?style=for-the-badge&logo=google">
</p>

---

## 📚 Sobre o Projeto

O **TutorIA** é uma plataforma educacional inteligente desenvolvida para auxiliar professores e alunos através do uso de Inteligência Artificial.

A aplicação combina uma API robusta em **FastAPI**, integração com modelos de IA **Google Gemini**, armazenamento local utilizando **SQLite** e uma interface moderna desenvolvida em **Next.js + TypeScript**.

O objetivo é oferecer uma experiência educacional personalizada, permitindo:

- Criação e organização de conteúdos;
- Apoio inteligente aos professores;
- Interação com assistente de IA;
- Gerenciamento de informações educacionais;
- Evolução para uma plataforma completa de ensino.

---

# 🏗️ Arquitetura do Projeto

```
TutorIA
│
├── backend
│   ├── API FastAPI
│   ├── Integração Gemini AI
│   ├── Banco SQLite
│   ├── Serviços da aplicação
│   └── Testes automatizados
│
├── frontend
│   ├── Next.js
│   ├── React + TypeScript
│   ├── Componentes reutilizáveis
│   └── Interface Professor/Aluno
│
├── docs
│   └── Documentação do projeto
│
└── archive
    └── Arquivos antigos e versões anteriores
```

---

# 🚀 Tecnologias

## Backend

| Tecnologia | Utilização |
|-|-|
| Python | Linguagem principal |
| FastAPI | Construção da API REST |
| Google Gemini | Inteligência Artificial |
| SQLite | Banco de dados |
| unittest | Testes automatizados |
| Uvicorn | Servidor ASGI |

---

## Frontend

| Tecnologia | Utilização |
|-|-|
| Next.js | Framework React |
| TypeScript | Tipagem estática |
| React | Componentização |
| CSS Modules | Estilização |
| npm | Gerenciamento de pacotes |

---

# ⚙️ Requisitos

Antes de iniciar, instale:

- Python **3.11 ou superior**
- Node.js **20 ou superior**
- npm
- Git

Verifique:

```bash
python --version

node --version

npm --version
```

---

# 📥 Instalação

Clone o projeto:

```bash
git clone https://github.com/GraziellaPereira/Hacktudo-TutorIA.git
```

Entre na pasta:

```bash
cd Hacktudo-TutorIA
```

---

# 🐍 Configuração Backend

Entre no backend:

```powershell
Set-Location backend
```

---

## Criar ambiente virtual

```powershell
python -m venv .venv
```

Ativar:

```powershell
.\.venv\Scripts\activate
```

---

## Instalar dependências

```powershell
pip install -r requirements.txt
```

---

# 🔑 Configuração Gemini AI

Crie um arquivo:

```
backend/.env
```

Configure:

```env
GEMINI_API_KEY=SUA_CHAVE_GEMINI
```

A chave pode ser criada através do Google AI Studio.

---

# ▶️ Executar Backend

Dentro da pasta `backend`:

```powershell
..\.venv\Scripts\python.exe -m uvicorn app.api.app:app --reload
```

API disponível:

```
http://localhost:8000
```

Documentação Swagger:

```
http://localhost:8000/docs
```

---

# 🌐 Configuração Frontend

Abra outro terminal:

```powershell
Set-Location frontend
```

---

## Instalar dependências

```bash
npm install
```

---

## Variáveis de ambiente

Criar:

```
frontend/.env.local
```

Exemplo:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

# ▶️ Executar Frontend

```bash
npm run dev
```

Aplicação:

```
http://localhost:3000
```

---

# 🧪 Testes Backend

Executar:

```powershell
Set-Location backend

..\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
```

Resultado esperado:

```
OK
```

---

# 📂 Estrutura Backend

```
backend
│
├── app
│   │
│   ├── api
│   │   └── Rotas FastAPI
│   │
│   ├── services
│   │   └── Serviços de IA e regras
│   │
│   ├── models
│   │   └── Modelos da aplicação
│   │
│   └── database
│       └── SQLite
│
├── tests
│   └── Testes automatizados
│
├── requirements.txt
└── .env
```

---

# 📂 Estrutura Frontend

```
frontend
│
├── app
│   └── Rotas Next.js
│
├── components
│   └── Componentes React
│
├── styles
│   └── CSS Modules
│
├── public
│   └── Arquivos públicos
│
├── package.json
└── .env.local
```

---

# 🤖 Inteligência Artificial

O TutorIA utiliza o Google Gemini para fornecer recursos inteligentes.

Possíveis aplicações:

- Assistente virtual educacional;
- Criação automática de conteúdos;
- Sugestão de atividades;
- Auxílio ao professor;
- Personalização do aprendizado.

---

# 🔄 Fluxo da Aplicação

```
              Usuário
                 |
                 |
                 ↓
        Next.js Frontend
                 |
                 |
                 ↓
          FastAPI Backend
                 |
        -----------------
        |               |
        ↓               ↓
    Gemini AI       SQLite
```

---

# 🔒 Segurança

Boas práticas implementadas:

- Variáveis sensíveis através de `.env`;
- Separação Frontend/Backend;
- API organizada por responsabilidades;
- Preparação para autenticação futura.

---

# 🛣️ Roadmap

## Concluído

✅ Estrutura Backend/Frontend  
✅ API FastAPI  
✅ Banco SQLite  
✅ Integração Gemini AI  
✅ Interface Professor/Aluno  
✅ Testes iniciais  

---

## Próximas etapas

⬜ Sistema completo de login  
⬜ Controle de usuários  
⬜ Dashboard educacional  
⬜ Histórico de conversas IA  
⬜ Upload de materiais didáticos  
⬜ Deploy em produção  

---

# 👨‍💻 Desenvolvimento

Executar ambiente completo:

Terminal 1:

```powershell
cd backend

..\.venv\Scripts\python.exe -m uvicorn app.api.app:app --reload
```

Terminal 2:

```bash
cd frontend

npm run dev
```

---

# 📌 Git Workflow

Atualizar projeto:

```bash
git add .

git commit -m "Descrição da alteração"

git push
```

---

# 🏆 Projeto

Desenvolvido para o desafio **Hacktudo**.

Projeto focado em unir:

- Educação;
- Inteligência Artificial;
- Desenvolvimento Web;
- Experiência personalizada de aprendizagem.

---

# 📄 Licença

Projeto desenvolvido para fins educacionais e tecnológicos.

# 🌐 Aplicação Online

O TutorIA está disponível para demonstração através do ambiente hospedado:

🔗 **Frontend:**  
https://hacktudo-frontend.onrender.com/

> ⚠️ **Observação sobre hospedagem**
>
> Atualmente o projeto está hospedado em uma infraestrutura com recursos limitados, destinada à apresentação e testes.
>
> Por esse motivo, a aplicação possui uma limitação de **1 usuário simultâneo por vez**.
>
> Caso outra pessoa tente acessar enquanto uma sessão de demonstração estiver em execução, pode ocorrer lentidão ou indisponibilidade temporária.
>
> Essa limitação está relacionada ao ambiente atual de hospedagem e não representa uma limitação da arquitetura do sistema.

---

# 🚀 Demonstração

Para testar o sistema:

1. Acesse:

```
https://hacktudo-frontend.onrender.com/
```

2. Aguarde o carregamento inicial da aplicação.

3. Utilize as funcionalidades disponíveis para professor e aluno.

> O primeiro acesso pode levar alguns segundos devido ao processo de inicialização do servidor hospedado.
