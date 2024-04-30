base_path=$1
dashboard_path=$2
port=$3
cd $base_path
export CSV_PATH="./data.csv"
echo "Starting dashboard on port $port"
streamlit run $dashboard_path --server.port $port
