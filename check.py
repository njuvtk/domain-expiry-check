import whois, datetime, requests, os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_msg(text):
    if BOT_TOKEN and CHAT_ID:
        r = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": text},
        )
        print("Telegram response:", r.text)  # 调试输出
    else:
        print("❌ BOT_TOKEN 或 CHAT_ID 未配置，消息未推送")

with open("domains.txt") as f:
    domains = [d.strip() for d in f if d.strip()]

now = datetime.datetime.now()

for domain in domains:
    try:
        w = whois.whois(domain)
        exp = w.expiration_date
        if isinstance(exp, list):
            exp = exp[0]

        if exp is None:
            msg = f"⚠️ {domain} 未返回到期时间，可能不支持 WHOIS 查询"
            print(msg)
            send_msg(msg)
            continue

        days_left = (exp - now).days

        if days_left <= 30:
            msg = f"⚠️ 域名 {domain} 将在 {days_left} 天后到期 (到期日: {exp.date()})"
            print(msg)
            send_msg(msg)
        else:
            msg = f"✅ {domain} 还剩 {days_left} 天到期 (到期日: {exp.date()})"
            print(msg)
            # 这里要不要推送，看你需求（可以只打印，不推送）
    except Exception as e:
        msg = f"❌ 查询 {domain} 失败: {e}"
        print(msg)
        send_msg(msg)