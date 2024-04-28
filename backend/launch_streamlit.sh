source .venv/Scripts/activate
data_path=$1
dashboard_path=$2
port=$3

export CSV_PATH=$data_path

echo "Starting dashboard on port $port"

.venv/Scripts/streamlit.exe run $dashboard_path --server.port $port