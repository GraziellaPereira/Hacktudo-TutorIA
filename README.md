# TutorIA

Projeto separado em dois aplicativos:

- `backend/`: API FastAPI, Gemini, SQLite e testes.
- `frontend/`: aplicação Next.js para as interfaces de professor e aluno.
- `docs/`: documentação complementar.
- `archive/`: scaffolds e cópias antigas.

## Backend

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m uvicorn app.api.app:app --reload
```

## Frontend

```powershell
Set-Location frontend
npm run dev
```

## Testes da API

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
```
