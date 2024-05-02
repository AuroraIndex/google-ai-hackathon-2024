cd backend
source .venv/bin/activate
uvicorn app.main:app --ws-max-size 110000000 &

cd ../client 
npm run dev
