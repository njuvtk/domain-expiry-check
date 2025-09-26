import whois, datetime, requests, os

# Telegram 配置（从 GitHub Secrets 里读取）
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# 读取域名列表
with open("domains.txt") as f:
    domains = [d.strip() for d in f if d.strip()]

now = datetime.datetime.now()

for domain in domains:
    try:
        w = whois.whois(domain)
        exp = w.expiration_date
        if isinstance(exp, list):
            exp = exp[0]

        days_left = (exp - now).days

        if days_left <= 30:
            msg = f"⚠️ 域名 {domain} 将在 {days_left} 天后到期 (到期日: {exp.date()})"
            print(msg)

            if BOT_TOKEN and CHAT_ID:
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                    data={"chat_id": CHAT_ID, "text": msg},
                )
        else:
            print(f"✅ {domain} 还剩 {days_left} 天到期 (到期日: {exp.date()})")

    except Exception as e:
        print(f"❌ 查询 {domain} 失败: {e}")