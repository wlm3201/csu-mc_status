import os
import base64
from datetime import datetime
import pytz
import requests
from mcstatus import JavaServer

vanilla = "csu-mc.org"
mod = "mod.csu-mc.org"
dbowner = "wlm3201"
dbname = "csu-mc_status.db"
db_url = "https://api.dbhub.io"
apikey = os.environ.get("apikey")


def dbhub(statement, relative):
    sql = base64.b64encode(statement.encode("utf-8"))
    payload = {"apikey": apikey, "dbowner": dbowner, "dbname": dbname, "sql": sql}
    r = requests.post(db_url + relative, data=payload)
    print(r.text)
    return r.text


def lookup_online(server):
    count = JavaServer.lookup(server).status().players.online
    print(count)
    statement = f'INSERT INTO online_stats (server, date, hour, count) VALUES ("{server}", "{date}", {hour}, {count})'
    dbhub(statement, "/v1/execute")


if __name__ == "__main__":
    curr_time = datetime.now(pytz.timezone("Asia/Shanghai"))
    date = curr_time.strftime("%Y-%m-%d")
    hour = curr_time.hour
    print(date, " ", hour)
    lookup_online(vanilla)
    lookup_online(mod)
