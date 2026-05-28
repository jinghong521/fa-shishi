from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# ===================== 配置 =====================
DASHSCOPE_API_KEY = "sk-d9dbe5af52d248f8be047e8959df457f"
TOTAL_POINTS = 6000
USED_POINTS = 169
# 全局存储对话上下文（单用户简易版）
chat_history = []
# ==================================================

@app.route('/')
def index():
    # 进入页面清空历史，开启新会话
    global chat_history
    chat_history = []
    remaining = TOTAL_POINTS - USED_POINTS
    return render_template('index.html', remaining_points=remaining, total_points=TOTAL_POINTS)

@app.route('/chat', methods=['POST'])
def chat():
    global chat_history
    try:
        data = request.get_json()
        prompt = data.get("prompt", "").strip()
        deep_thinking = data.get("deep_thinking", False)

        if not prompt:
            return jsonify({"code": 400, "reply": "请输入内容"})

        # 追加当前用户提问到上下文
        chat_history.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
            "Content-Type": "application/json"
        }

        system_content = "你是法时时AI助手，专业、简洁、合规。"
        if deep_thinking:
            system_content += " 请开启深度思考，严谨分析。"

        # 拼接完整会话消息
        messages = [{"role": "system", "content": system_content}] + chat_history

        payload = {
            "model": "qwen-turbo",
            "messages": messages
        }

        resp = requests.post(
            "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        res_json = resp.json()

        if "choices" in res_json:
            ai_reply = res_json["choices"][0]["message"]["content"]
            # 追加AI回复到上下文，实现多轮记忆
            chat_history.append({"role": "assistant", "content": ai_reply})
            return jsonify({"code": 200, "reply": ai_reply})
        else:
            return jsonify({"code": 500, "reply": f"API错误：{res_json}"})

    except Exception as e:
        return jsonify({"code": 500, "reply": f"错误：{str(e)}"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)