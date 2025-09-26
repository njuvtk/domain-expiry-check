import whois, datetime, requests, os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_msg(text):
    if BOT_TOKEN and CHAT_ID:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"},
        )

def query_local_whois(domain):
    try:
        w = whois.whois(domain)
        exp = w.expiration_date
        if isinstance(exp, list):
            exp = exp[0]
        return exp
    except:
        return None

def query_shreshtait(domain):
    try:
        url = f"https://domaininfo.shreshtait.com/api/search/{domain}"
        resp = requests.get(url).json()
        exp = resp.get("expiration_date")
        if exp:
            return datetime.datetime.fromisoformat(exp.split("T")[0])
    except:
        return None

def query_whoxy(domain):
    try:
        url = f"https://www.whoxy.com/free-whois-api/?domain={domain}"
        resp = requests.get(url).json()
        exp = resp.get("expiration_date")
        if exp:
            return datetime.datetime.fromisoformat(exp.split("T")[0])
    except:
        return None

def query_fallback(domain):
    exp = query_local_whois(domain)
    if exp is None:
        exp = query_shreshtait(domain)
    if exp is None:
        exp = query_whoxy(domain)
    return exp

# ----------------
domains = []
with open("domains.txt") as f:
    domains = [d.strip() for d in f if d.strip()]

now = datetime.datetime.now()
urgent, warning, safe, unknown = [], [], [], []

for domain in domains:
    exp = query_fallback(domain)
    if exp is None:
        unknown.append(f"⚠️ *{domain}* 未返回到期时间或查询失败")
        continue

    days_left = (exp - now).days
    if days_left < 7:
        urgent.append((days_left, f"🚨 *{domain}* ⚠️ *仅剩 {days_left} 天!* (到期日: `{exp.date()}`)"))
    elif days_left <= 30:
        warning.append((days_left, f"⚠️ *{domain}* 将在 *{days_left} 天* 后到期 (到期日: `{exp.date()}`)"))
    else:
        safe.append((days_left, f"✅ *{domain}* 剩余 *{days_left} 天* (到期日: `{exp.date()}`)"))

# 排序
urgent.sort(key=lambda x: x[0])
warning.sort(key=lambda x: x[0])
safe.sort(key=lambda x: x[0])

sections = []
if urgent:
    sections.append("*🚨 紧急 (<7天)*\n" + "\n".join(msg for _, msg in urgent))
if warning:
    sections.append("*⚠️ 警告 (7~30天)*\n" + "\n".join(msg for _, msg in warning))
if safe:
    sections.append("*✅ 安全 (>30天)*\n" + "\n".join(msg for _, msg in safe))
if unknown:
    sections.append("*⚠️ 未知 / 查询失败*\n" + "\n".join(unknown))

final_report = "📢 *域名到期检测报告*\n\n" + "\n\n".join(sections)
print(final_report)
send_msg(final_report)