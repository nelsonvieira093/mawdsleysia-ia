# Mawdsleys Executive OS

Backend + AI Engine + Frontend

Terminal 1 - Backend:

bash
cd E:\MAWDSLEYS-AGENTE
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
Terminal 2 - Frontend:

bash
cd E:\MAWDSLEYS-AGENTE\frontend
npm run dev


# Navegue até a pasta do projeto onde está o venv
cd E:\MAWDSLEYS-AGENTE


# Ative o ambiente virtual
venv\Scripts\activate


📍 Diretório: E:\MAWDSLEYS-AGENTE\backend
venv\Scripts\activate
uvicorn main:app --reload


uvicorn main:app --host 0.0.0.0 --port $PORT

(venv) PS E:\MAWDSLEYS-AGENTE\backend> 
uvicorn main:app --host 0.0.0.0 --port 8000 --reload




 E:\MAWDSLEYS-AGENTE> venv\Scripts\activate
>> uvicorn backend.main:app --reload

docker compose down -v
docker compose up --build


docker compose restart backend
docker compose restart backend

docker compose up --build


SOLUÇÃO 1 (a mais simples — recomendo)

Entre na pasta backend e rode o comando de lá.

1️⃣ Vá para a pasta correta
cd backend


Confirme:

ls


Você DEVE ver:

main.py
database/
models/
api/

2️⃣ Agora rode o Uvicorn
uvicorn main:app --reload

✅ SOLUÇÃO 2 (rodar da raiz, sem cd)

Se quiser rodar da raiz do projeto:

uvicorn backend.main:app --reload



🚀 1. INICIE O SERVIDOR AGORA:
bash
cd /e/MAWDSLEYS-AGENTE/backend
python main.py
OU se tiver um comando específico:

bash
# Tente estas opções se "python main.py" não funcionar:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
# ou
fastapi dev main.py
# ou
python -m uvicorn main:app --reload

./ngrok.exe http --domain=mawdsleysia-ia.ngrok.io 8000


uvicorn backend.api.main:app --host 127.0.0.1 --port 8000 --reload
PS E:\MAWDSLEYS-AGENTE>


uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload

 E:\MAWDSLEYS-AGENTE> venv\Scripts\activate
>> uvicorn backend.main:app --reload
comaando para ver versão do Fly

& "$env:USERPROFILE\.fly\bin\flyctl.exe" version

#Para abrir FLy
& "$env:USERPROFILE\.fly\bin\flyctl.exe" auth login

A sequência é sempre:

git add
git commit
git push

/c/Users/Nelson\ Vieira/.fly/bin/flyctl.exe deploy
