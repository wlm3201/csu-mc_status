import os
import base64
from datetime import datetime, timedelta
import requests
import pytz
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import interp1d

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
    return r.json()


def day(server, color):
    yesterday = today - timedelta(days=1)
    yesterday = yesterday.strftime("%Y-%m-%d")
    statment = f'SELECT hour , count FROM online_stats WHERE server = "{server}" AND date= "{yesterday}" ORDER BY hour'
    data = dbhub(statment, "/v1/query")
    data = [[int(i[0]["Value"]), int(i[1]["Value"])] for i in data]
    hours = np.arange(0, 24)
    counts = np.zeros(24)
    for i in data:
        counts[i[0]] = i[1]
    f = interp1d(hours, counts, kind="next")
    minites = np.linspace(0, 23, num=23 * 60)
    plt.plot(hours, counts, ".", minites, f(minites), "-", label=server, color=color)
    plt.legend()
    plt.xticks(hours)


def week(server):
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    statment = f'SELECT strftime("%w", date) as day ,hour, count FROM online_stats WHERE server = "{server}" AND date BETWEEN "{week_start.strftime("%Y-%m-%d")}" AND "{week_end.strftime("%Y-%m-%d")}" ORDER BY date '
    data = dbhub(statment, "/v1/query")
    data = [[int(i[0]["Value"]), int(i[1]["Value"]), int(i[2]["Value"])] for i in data]
    heatmap = np.zeros((24, 7), dtype=int)
    for i in data:
        heatmap[i[1]][i[0]] = i[2]
    plt.imshow(heatmap, cmap="hot", interpolation="bicubic")
    plt.title(server + " 周活")
    plt.xticks(ticks=np.arange(0, 7), labels=np.arange(1, 8))
    plt.yticks(ticks=np.arange(0, 24), labels=np.arange(1, 25))
    plt.colorbar()
    plt.savefig(f"plots/周活_{server}_{(today.day - 1) // 7 + 1}.png")
    plt.clf()


def month(server):
    date = today.strftime("%Y-%m")
    offset = today.replace(day=1).weekday()
    statment = f'SELECT strftime("%d", date) as day, MAX(count) as count FROM online_stats WHERE server="{server}" and date LIKE "{date}%" GROUP BY date'
    data = dbhub(statment, "/v1/query")
    data = [[int(i[0]["Value"]), int(i[1]["Value"])] for i in data]
    heatmap = np.zeros(42, dtype=int)
    for i in data:
        heatmap[i[0] - 1 + offset] = i[1]
    heatmap = heatmap.reshape(6, 7)
    if np.all(heatmap[-1] == 0):
        heatmap = heatmap[:-1]
    plt.imshow(heatmap, cmap="hot", interpolation="nearest")
    plt.title(server + " 月活")
    plt.xticks(ticks=np.arange(0, 7), labels=np.arange(1, 8))
    plt.colorbar()
    for i in range(heatmap.shape[0]):
        for j in range(heatmap.shape[1]):
            plt.text(j, i, heatmap[i, j], ha="center", va="center")
    plt.savefig(f"plots/月活_{server}_{date}.png")
    plt.clf()


if __name__ == "__main__":
    today = datetime.now(pytz.timezone("Asia/Shanghai"))
    os.makedirs("plots", exist_ok=1)
    plt.rcParams["font.family"] = ["SimHei"]
    day(vanilla, "c")
    day(mod, "m")
    plt.savefig(f"plots/日活.png")
    if today.weekday() == 0:
        week(vanilla)
        week(mod)
    if today.day == 1:
        month(vanilla)
        month(mod)
