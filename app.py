# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, render_template, Response
import requests
import json
import os
import random
import base64
import re

app = Flask(__name__)

# 从配置文件中settings加载配置
app.config.from_pyfile('settings.py')


@app.route("/", methods=["GET"])
def index():
    return render_template("chat.html")


@app.route("/chat", methods=["POST"])
def chat():
    global user_text
    messages = request.form.get("prompts", None)
    apiKey = request.form.get("apiKey", None)
    model = request.form.get("model", "gpt-3.5-turbo-0125")
    temperature = request.form.get("temperature", 0.5)
    max_tokens = request.form.get("max_tokens", 4000)
    password = request.form.get("password", None)
    api_url = request.form.get("api_url", None)

    if api_url is None:
        api_url = app.config.get("API_URL", None)

    # 如果模型不包含"gpt-4"和"dall-e-3"，使用默认的API_KEYS
    if apiKey is None:
        if "gpt-4" not in model and "dall-e-3" not in model:
            api_keys = app.config.get("API_KEYS", [])
            apiKey = os.environ.get('OPENAI_API_KEY', random.choice(api_keys))

    # 如果模型包含"gpt-4"或者dall-e-3，密码错误则返回错误！
    if apiKey is None:
        if "gpt-4" in model or "dall-e-3" in model:
            if not password:
                return jsonify({"error": {"message": "请联系群主获取授权码或者输入自己的apikey！！！",
                                          "type": "empty_password_error", "code": ""}})
    if apiKey is None:
        if "gpt-4" in model or "dall-e-3" in model:
            if password not in ["授权码1", "授权码2", "授权码3", "授权码4", "授权码5"]:
                return jsonify({
                    "error": {
                        "message": "请检查并输入正确的授权码或者输入自己的apikey！！！",
                        "type": "invalid_password_error",
                        "code": ""
                    }
                })

    if apiKey is None:
        if "gpt-4" in model or "dall-e-3" in model:
            if password == "授权码1":
                api_keys = app.config.get("API_KEYS1", [])
                apiKey = os.environ.get('OPENAI_API_KEY', random.choice(api_keys))
                api_url = app.config.get("API_URL1", None)
            else:
                if password == "授权码2":
                    api_keys = app.config.get("API_KEYS2", [])
                    apiKey = os.environ.get('OPENAI_API_KEY', random.choice(api_keys))
                    api_url = app.config.get("API_URL2", None)
                elif password == "授权码3":
                    api_keys = app.config.get("API_KEYS3", [])
                    apiKey = os.environ.get('OPENAI_API_KEY', random.choice(api_keys))
                    api_url = app.config.get("API_URL3", None)
                elif password == "授权码4":
                    api_keys = app.config.get("API_KEYS4", [])
                    apiKey = os.environ.get('OPENAI_API_KEY', random.choice(api_keys))
                    api_url = app.config.get("API_URL4", None)
                elif password == "授权码5":
                    api_keys = app.config.get("API_KEYS5", [])
                    apiKey = os.environ.get('OPENAI_API_KEY', random.choice(api_keys))
                    api_url = app.config.get("API_URL5", None)

    # 如果模型包含 "xxx"，更换对应的api_url和data
    if model == "dall-e-2":
        api_url += "/v1/images/generations"
        data = {
            "model": "dall-e-2",
            "prompt": messages,
            "n": 1,
            "size": "256x256",
        }
    elif model == "dall-e-2-m":
        api_url += "/v1/images/generations"
        data = {
            "model": "dall-e-2",
            "prompt": messages,
            "n": 1,
            "size": "512x512",
        }
    elif model == "dall-e-2-l":
        api_url += "/v1/images/generations"
        data = {
            "model": "dall-e-2",
            "prompt": messages,
            "n": 1,
            "size": "1024x1024",
        }
    elif model == "dall-e-3":
        api_url += "/v1/images/generations"
        data = {
            "model": "dall-e-3",
            "prompt": messages,
            "n": 1,
            "size": "1024x1024",
            "quality": "standard",
            "style": "natural",
        }
    elif model == "dall-e-3-w":
        api_url += "/v1/images/generations"
        data = {
            "model": "dall-e-3",
            "prompt": messages,
            "n": 1,
            "size": "1792x1024",
            "quality": "standard",
            "style": "natural",
        }
    elif model == "dall-e-3-l":
        api_url += "/v1/images/generations"
        data = {
            "model": "dall-e-3",
            "prompt": messages,
            "n": 1,
            "size": "1024x1792",
            "quality": "standard",
            "style": "natural",
        }
    elif model == "dall-e-3-hd":
        api_url += "/v1/images/generations"
        data = {
            "model": "dall-e-3",
            "prompt": messages,
            "n": 1,
            "size": "1024x1024",
            "quality": "hd",
            "style": "natural",
        }
    elif model == "dall-e-3-w-hd":
        api_url += "/v1/images/generations"
        data = {
            "model": "dall-e-3",
            "prompt": messages,
            "n": 1,
            "size": "1792x1024",
            "quality": "hd",
            "style": "natural",
        }
    elif model == "dall-e-3-l-hd":
        api_url += "/v1/images/generations"
        data = {
            "model": "dall-e-3",
            "prompt": messages,
            "n": 1,
            "size": "1024x1792",
            "quality": "hd",
            "style": "natural",
        }
    elif model == "dall-e-3-v":
        api_url += "/v1/images/generations"
        data = {
            "model": "dall-e-3",
            "prompt": messages,
            "n": 1,
            "size": "1024x1024",
            "quality": "standard",
            "style": "vivid",
        }
    elif model == "dall-e-3-w-v":
        api_url += "/v1/images/generations"
        data = {
            "model": "dall-e-3",
            "prompt": messages,
            "n": 1,
            "size": "1792x1024",
            "quality": "standard",
            "style": "vivid",
        }
    elif model == "dall-e-3-l-v":
        api_url += "/v1/images/generations"
        data = {
            "model": "dall-e-3",
            "prompt": messages,
            "n": 1,
            "size": "1024x1792",
            "quality": "standard",
            "style": "vivid",
        }
    elif model == "dall-e-3-p":
        api_url += "/v1/images/generations"
        data = {
            "model": "dall-e-3",
            "prompt": messages,
            "n": 1,
            "size": "1024x1024",
            "quality": "hd",
            "style": "vivid",
        }
    elif model == "dall-e-3-w-p":
        api_url += "/v1/images/generations"
        data = {
            "model": "dall-e-3",
            "prompt": messages,
            "n": 1,
            "size": "1792x1024",
            "quality": "hd",
            "style": "vivid",
        }
    elif model == "dall-e-3-l-p":
        api_url += "/v1/images/generations"
        data = {
            "model": "dall-e-3",
            "prompt": messages,
            "n": 1,
            "size": "1024x1792",
            "quality": "hd",
            "style": "vivid",
        }
    elif "text-moderation" in model:
        api_url += "/v1/moderations"
        data = {
            "input": messages,
            "model": model,
        }
    elif "text-embedding" in model:
        api_url += "/v1/embeddings"
        data = {
            "input": messages,
            "model": model,
        }
    elif "tts-1" in model:
        api_url += "/v1/audio/speech"
        data = {
            "input": messages.replace("user", "").replace("content", "").replace("role", "").replace("assistant", ""),
            "model": model,
            "voice": "alloy",
        }

    elif "gpt-3.5-turbo-instruct" in model or "babbage-002" in model or "davinci-002" in model:
        api_url += "/v1/completions"
        data = {
            "prompt": messages,
            "model": model,
            "max_tokens": int(max_tokens),
            "temperature": float(temperature),
            "top_p": 1,
            "n": 1,
            "stream": True,
        }
    elif model == "gpt-4-vision-preview":
        image_url_match = re.search(r'https://\S+,', messages)
        image_url = image_url_match.group().strip(",") if image_url_match else None

        try:
            messages = json.loads(messages)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")

        # Extract URL and content using regex
        regex_pattern = r"https://[^,]+,(.+)"

        for message in messages:
            if isinstance(message, dict):
                content = message.get("content", "")
            elif isinstance(message, str):
                try:
                    message_dict = json.loads(message)
                    content = message_dict.get("content", "")
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON in message: {e}")
                    content = ""
            else:
                content = ""

            match = re.search(regex_pattern, content)

            if match:
                user_text = match.group(1)

        api_url += "/v1/chat/completions"
        data = {
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_text},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url":
                                    image_url,
                            },
                        },
                    ],
                }
            ],
            "model": model,
            "max_tokens": int(max_tokens),
        }
    else:
        # 对于其他模型，使用原有 api_url
        api_url += "/v1/chat/completions"
        data = {
            "messages": json.loads(messages),
            "model": model,
            "max_tokens": int(max_tokens),
            "temperature": float(temperature),
            "top_p": 1,
            "n": 1,
            "stream": True,
        }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {apiKey}",
    }

    try:
        resp = requests.post(
            url=api_url,
            headers=headers,
            json=data,
            stream=True,
            timeout=(60, 60)
        )
    except requests.exceptions.Timeout:
        return jsonify({"error": {"message": "Request timeout", "type": "timeout_error", "code": ""}})
    except Exception as e:
        return jsonify({"error": {"message": str(e), "type": "unexpected_error", "code": ""}})

    # 接收图片url
    if "dall-e" in model:
        response_data = json.loads(resp.content.decode('utf-8'))
        image_url = response_data["data"][0]["url"]
        # 返回图片url
        return jsonify(image_url)

    # text-moderation，接收审查结果
    if "text-moderation" in model:
        response_data = json.loads(resp.content.decode('utf-8'))
        moderation_results = response_data["results"]

        # 提取每个结果的内容并按顺序存储在列表中
        result_list = []
        for result in moderation_results:
            result_data = {
                "有害标记": result["flagged"],
                "违规类别": {
                    "仇恨": result["categories"]["hate"],
                    "威胁性仇恨": result["categories"]["hate/threatening"],
                    "骚扰": result["categories"]["harassment"],
                    "威胁性骚扰": result["categories"]["harassment/threatening"],
                    "自残": result["categories"]["self-harm"],
                    "自残意图": result["categories"]["self-harm/intent"],
                    "自残说明": result["categories"]["self-harm/instructions"],
                    "性内容": result["categories"]["sexual"],
                    "未成年人性内容": result["categories"]["sexual/minors"],
                    "暴力": result["categories"]["violence"],
                    "图文暴力": result["categories"]["violence/graphic"]
                },
                "违规类别分数(越大置信度越高)": {
                    "仇恨分数": result["category_scores"]["hate"],
                    "威胁性仇恨分数": result["category_scores"]["hate/threatening"],
                    "骚扰分数": result["category_scores"]["harassment"],
                    "威胁性骚扰分数": result["category_scores"]["harassment/threatening"],
                    "自残分数": result["category_scores"]["self-harm"],
                    "自残意图分数": result["category_scores"]["self-harm/intent"],
                    "自残说明分数": result["category_scores"]["self-harm/instructions"],
                    "性内容分数": result["category_scores"]["sexual"],
                    "未成年人性内容分数": result["category_scores"]["sexual/minors"],
                    "暴力分数": result["category_scores"]["violence"],
                    "图文暴力分数": result["category_scores"]["violence/graphic"]
                },
            }
            result_list.append(result_data)

        # 返回包含所有结果的列表，并将其转换为可读的字符串
        return json.dumps(result_list, ensure_ascii=False)

    # text-embedding，接收多维数组
    if "text-embedding" in model:
        response_data = json.loads(resp.content.decode('utf-8'))
        embedding = response_data["data"][0]["embedding"]
        return jsonify(embedding)

    # 图像识别
    if "gpt-4-vision-preview" in model:
        # 在解析响应数据后
        response_data = json.loads(resp.content.decode('utf-8'))
        vs = response_data["choices"][0]["message"]["content"]
        return json.dumps(vs, ensure_ascii=False).strip('"').replace('\\n', '')

    # 在TTS模型的情况下，返回base64编码的音频数据
    if "tts-1" in model:
        # 解析响应的音频数据并进行base64编码
        audio_data = base64.b64encode(resp.content).decode('utf-8')
        return jsonify(audio_data)

    # gpt模型回复接收
    def generate():
        errorStr = ""
        for chunk in resp.iter_lines():
            if chunk:
                streamStr = chunk.decode("utf-8").replace("data: ", "")
                try:
                    streamStr = streamStr.strip("[DONE]")
                    streamDict = json.loads(streamStr)
                except:
                    errorStr += streamStr.strip()
                    continue

                if "choices" in streamDict:
                    delData = streamDict["choices"][0]
                    if "finish_reason" in delData and delData["finish_reason"] is not None:
                        break
                    else:
                        if "text" in delData:
                            respStr = delData["text"]
                            yield respStr
                        # 添加下面这段代码以处理包含 "delta" 的新返回数据格式
                        elif "delta" in delData and "content" in delData["delta"]:
                            respStr = delData["delta"]["content"]
                            yield respStr
                else:
                    errorStr += f"Unexpected data format: {streamDict}"

        if errorStr != "":
            with app.app_context():
                yield errorStr

    return Response(generate(), content_type='application/octet-stream')


if __name__ == '__main__':
    app.run('0.0.0.0', 80)
