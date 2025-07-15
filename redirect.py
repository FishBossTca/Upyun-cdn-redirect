#!/usr/bin/env python3
import requests
import json
import sys
import re
import argparse

# ========= 可配置参数部分 =========
USERNAME = "又拍云账户"
PASSWORD = "又拍云密码"
BUCKET_NAME = "服务名称"
RULE_NAMES = ["重定向1", "重定向2"]
NEW_PORT = "9999"  # 默认端口号

# ========= 固定接口配置 =========
LOGIN_URL = "https://console.upyun.com/accounts/signin/"
REWRITE_GET_URL = f"https://console.upyun.com/api/v2/rewrite?bucket_name={BUCKET_NAME}"
REWRITE_POST_URL = "https://console.upyun.com/api/v2/rewrite"

session = requests.Session()

def login():
    print("[1] 正在登录...")
    headers = {"Content-Type": "application/json"}
    data = {"username": USERNAME, "password": PASSWORD}
    resp = session.post(LOGIN_URL, json=data, headers=headers)
    if resp.status_code != 200:
        print("[×] 登录失败，HTTP 状态码:", resp.status_code)
        sys.exit(1)

    if not session.cookies.get("s"):
        print("[×] 登录失败，无法获取 cookie，请检查用户名和密码是否正确")
        sys.exit(1)
    print("[√] 登录成功，cookie 获取成功")

def get_rewrite_config():
    print("[2] 正在获取 Bucket 配置...")
    resp = session.get(REWRITE_GET_URL)
    if resp.status_code != 200:
        print("[×] 获取 rewrite 配置失败，HTTP 状态码:", resp.status_code)
        sys.exit(1)
    data = resp.json()
    if "data" not in data or "rewrite" not in data["data"]:
        print("[×] 未能获取 rewrite 配置，请检查 BUCKET_NAME 是否正确")
        sys.exit(1)
    return data["data"]["rewrite"]

def update_rule(rule, port):
    rewrite_id = rule.get("rewrite_id")
    describe = rule.get("describe")
    print(f"[→] 匹配规则：{describe}（ID: {rewrite_id}）")

    content = rule.get("content", {})
    actions = content.get("actions", [])
    for action in actions:
        target = action.get("target", "")
        new_target = re.sub(r":[0-9]+", f":{port}", target)
        action["target"] = new_target
    content["actions"] = actions

    final_json = {
        "describe": describe,
        "type": "general",
        "priority": rule.get("priority"),
        "break": rule.get("break"),
        "status": "ON",
        "rewrite_id": rewrite_id,
        "content": content
    }

    headers = {"Content-Type": "application/json"}
    resp = session.post(REWRITE_POST_URL, json=final_json, headers=headers)
    if resp.status_code != 200:
        print(f"[×] 规则 \"{describe}\" 修改失败，HTTP 状态码: {resp.status_code}")
        return

    resp_json = resp.json()
    if isinstance(resp_json.get("data"), dict):
        print(f"[√] 规则 \"{describe}\" 修改成功")
    else:
        msg = resp_json.get("data", {}).get("message", "未知错误") if resp_json.get("data") else "未知错误"
        print(f"[×] 规则 \"{describe}\" 修改失败：{msg}")

def main():
    parser = argparse.ArgumentParser(description="又拍云 rewrite 规则端口修改脚本")
    parser.add_argument("-p", "--port", help="新的端口号，覆盖默认值")
    args = parser.parse_args()

    port = args.port if args.port else NEW_PORT

    login()
    rewrite_rules = get_rewrite_config()

    print("[3] 正在处理规则...")
    for name in RULE_NAMES:
        rule = next((r for r in rewrite_rules if r.get("describe") == name), None)
        if rule is None:
            print(f"[!] 规则 \"{name}\" 未找到，跳过")
            continue
        update_rule(rule, port)

    print("[完成] 所有规则处理完毕。")

if __name__ == "__main__":
    main()
