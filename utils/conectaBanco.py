import psycopg2

def conectaBanco(username, password):
    conn = psycopg2.connect(
        dbname="nsylumeserfsothlrrcs",
        user=username,
        password=password,
        host="nsylumeserfsothlrrcs.db.sa-east-1.nhost.run", 
        port="5432"
    )
    cursor = conn.cursor()
    return conn, cursor