import whois, datetime, requests, os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_msg(text):
    if BOT_TOKEN and CHAT_ID:
        r = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": text,
                "parse_mode": "Markdown"  # 使用 Markdown
            },
        )
        print("Telegram response:", r.text)
    else:
        print("❌ BOT_TOKEN 或 CHAT_ID 未配置，消息未推送")

with open("domains.txt") as f:
    domains = [d.strip() for d in f if d.strip()]

now = datetime.datetime.now()

urgent, warning, safe, unknown = [], [], [], []

for domain in domains:
    try:
        w = whois.whois(domain)
        exp = w.expiration_date
        if isinstance(exp, list):
            exp = exp[0]

        if exp is None:
            msg = f"⚠️ *{domain}* 未返回到期时间，可能不支持 WHOIS"
            unknown.append(msg)
            continue

        days_left = (exp - now).days

        if days_left < 7:
            msg = f"🚨 *{domain}* ⚠️ *仅剩 {days_left} 天!* (到期日: `{exp.date()}`)"
            urgent.append((days_left, msg))
        elif days_left <= 30:
            msg = f"⚠️ *{domain}* 将在 *{days_left} 天* 后到期 (到期日: `{exp.date()}`)"
            warning.append((days_left, msg))
        else:
            msg = f"✅ *{domain}* 剩余 *{days_left} 天* (到期日: `{exp.date()}`)"
            safe.append((days_left, msg))

    except Exception as e:
        msg = f"❌ *{domain}* 查询失败: `{e}`"
        unknown.append(msg)

# 排序：剩余天数升序
urgent.sort(key=lambda x: x[0])
warning.sort(key=lambda x: x[0])
safe.sort(key=lambda x: x[0])

# 拼接最终报告
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