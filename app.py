  # -*- coding: utf-8 -*-
from datetime import datetime,timedelta 
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

@app.route("/default_balance", methods=["GET"])
def get_default_balance():
    # 从配置文件中获取默认的 API_KEY 和 API_URL
    api_keys = app.config.get("API_KEYS1", [])
    apiKey = os.environ.get('OPENAI_API_KEY', random.choice(api_keys))
    apiUrl = app.config.get("API_URL1", None)

    # 如果默认的 apiKey 或 apiUrl 为空，返回错误信息
    if not apiKey or not apiUrl:
        return jsonify({"error": {"message": "No default API key or URL set", "type": "config_error", "code": ""}})

    headers = {
        "Authorization": f"Bearer {apiKey}",
        "Content-Type": "application/json"
    }

    # 获取余额信息
    try:
        subscription_url = f"{apiUrl}/v1/dashboard/billing/subscription"
        subscription_resp = requests.get(subscription_url, headers=headers)
        subscription_data = subscription_resp.json()

        total = subscription_data.get('hard_limit_usd', 0)

        # 获取使用情况
        start_date = datetime.now() - timedelta(days=99)
        end_date = datetime.now()

        usage_url = f"{apiUrl}/v1/dashboard/billing/usage?start_date={start_date.strftime('%Y-%m-%d')}&end_date={end_date.strftime('%Y-%m-%d')}"
        usage_resp = requests.get(usage_url, headers=headers)
        usage_data = usage_resp.json()

        total_usage = usage_data.get('total_usage', 0) / 100

        remaining = total - total_usage

        return jsonify({
            "total_balance": total,
            "used_balance": total_usage,
            "remaining_balance": remaining
        })
    except Exception as e:
        return jsonify({"error": {"message": str(e), "type": "api_error", "code": ""}})


@app.route("/chat", methods=["POST"])
def chat():
    global user_text
    messages = request.form.get("prompts", None)
    apiKey = request.form.get("apiKey", None)
    model = request.form.get("model", "gpt-4o-mini")
    temperature = request.form.get("temperature", 0.5)
    max_tokens = request.form.get("max_tokens", 4000)
    password = request.form.get("password", None)
    api_url = request.form.get("api_url", None)
    image_base64 = request.form.get("image_base64", None)
    # 获取当前日期和时间
    current_time = datetime.now().strftime("%Y年%m月%d日%H:%M:%S")

    # 获取当前日期
    current_date = datetime.now().strftime("%Y.%m.%d")

    # 获取当前脚本所在目录
    current_directory = os.path.dirname(os.path.realpath(__file__))
    # 构建文件夹路径
    folder_path = os.path.join(current_directory, "对话记录")

    # 如果对话记录文件夹不存在，则创建它
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # 构建文件保存路径
    file_name = f"{current_date}.txt"
    file_path = os.path.join(folder_path, file_name)

    # 将用户输入的message和model以及时间保存到一个文件
    with open(file_path, "a", encoding="utf-8") as all_info_file:
        all_info_file.write(f"Time: {current_time}\nModel: {model}\nApiKey: {apiKey}\nApi_url: {api_url}\nMessage: {messages}\n\n")

    if api_url is None:
        api_url = app.config.get("API_URL", None)

    # 如果模型不包含"gpt-4"和"dall-e-3"，使用默认的API_KEYS
    if apiKey is None:
       if "gpt-4" not in model and "dall" not in model and "claude" not in model and "SparkDesk" not in model and "gemini" not in model and "o1" not in model and "chatgpt" not in model and "embedding" not in model and "moderation" not in model and "glm" not in model and "yi" not in model and "commmand" not in model and "stable" not in model and "deep" not in model and "midjourney" not in model and "douubao" not in model and "qwen" not in model and "co" not in model and "suno" not in model and "abab" not in model and "chat" not in model:
            api_keys = app.config.get("API_KEYS", [])
            apiKey = os.environ.get('OPENAI_API_KEY', random.choice(api_keys))

    # 如果模型包含"gpt-4"或者dall-e-3，密码错误则返回错误！
    if apiKey is None:
        if "gpt-4" in model or "dall" in model or "claude" in model or "SparkDesk" in model or "gemini" in model or "o1" in model or "chatgpt" in model or "embedding" in model or "moderation" in model or "glm" in model or "yi" in model or "commmand" in model or "stable" in model or "deep" in model or "midjourney" in model or "douubao" in model or "qwen" in model or "co" in model or "suno" in model or "abab" in model or "chat" in model:
            if not password:
                return jsonify({"error": {"message": "请联系群主获取授权码或者输入自己的apikey！！！",
                                          "type": "empty_password_error", "code": ""}})
    if apiKey is None:
        if "gpt-4" in model or "dall" in model or "claude" in model or "SparkDesk" in model or "gemini" in model or "o1" in model or "chatgpt" in model or "embedding" in model or "moderation" in model or "glm" in model or "yi" in model or "commmand" in model or "stable" in model or "deep" in model or "midjourney" in model or "douubao" in model or "qwen" in model or "co" in model or "suno" in model or "abab" in model or "chat" in model:
            if password not in ["freegpt", "D2f9A7c5", "3E6bR8s1", "H4j7N9q2", "5T6gY1h9","L8m3W7e2"]:
                return jsonify({
                    "error": {
                        "message": "请检查并输入正确的授权码或者输入自己的apikey！！！",
                        "type": "invalid_password_error",
                        "code": ""
                    }
                })

    if apiKey is None:
        if "gpt-4" in model or "dall" in model or "claude" in model or "SparkDesk" in model or "gemini" in model or "o1" in model or "chatgpt" in model or "embedding" in model or "moderation" in model or "glm" in model or "yi" in model or "commmand" in model or "stable" in model or "deep" in model or "midjourney" in model or "douubao" in model or "qwen" in model or "co" in model or "suno" in model or "abab" in model or "chat" in model:
            if password == "freegpt":
                api_keys = app.config.get("API_KEYS1", [])
                apiKey = os.environ.get('OPENAI_API_KEY', random.choice(api_keys))
                api_url = app.config.get("API_URL1", None)
            else:
                if password == "D2f9A7c5":
                    api_keys = app.config.get("API_KEYS2", [])
                    apiKey = os.environ.get('OPENAI_API_KEY', random.choice(api_keys))
                    api_url = app.config.get("API_URL2", None)
                elif password == "3E6bR8s1":
                    api_keys = app.config.get("API_KEYS3", [])
                    apiKey = os.environ.get('OPENAI_API_KEY', random.choice(api_keys))
                    api_url = app.config.get("API_URL3", None)
                elif password == "H4j7N9q2":
                    api_keys = app.config.get("API_KEYS4", [])
                    apiKey = os.environ.get('OPENAI_API_KEY', random.choice(api_keys))
                    api_url = app.config.get("API_URL4", None)
                elif password == "5T6gY1h9":
                    api_keys = app.config.get("API_KEYS5", [])
                    apiKey = os.environ.get('OPENAI_API_KEY', random.choice(api_keys))
                    api_url = app.config.get("API_URL5", None)
                elif password == "L8m3W7e2":
                    api_keys = app.config.get("API_KEYS6", [])
                    apiKey = os.environ.get('OPENAI_API_KEY', random.choice(api_keys))
                    api_url = app.config.get("API_URL6", None)
    if apiKey is None:
        if password not in ["freegpt", "D2f9A7c5", "3E6bR8s1", "H4j7N9q2", "5T6gY1h9","L8m3W7e2"]:
            if "gizmo" in model:
                api_keys = app.config.get("API_KEYS7", [])
                apiKey = os.environ.get('OPENAI_API_KEY', random.choice(api_keys))
                api_url = app.config.get("API_URL7", None)
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
    elif model == "cogview-3":
        api_url += "/v1/images/generations"
        data = {
            "model": "cogview-3",
            "prompt": messages,
            "size": "1024x1024",
        }
    elif model == "cogview-3-plus":
        api_url += "/v1/images/generations"
        data = {
            "model": "cogview-3-plus",
            "prompt": messages,
            "size": "1024x1024",
        }
    elif "moderation" in model:
        api_url += "/v1/moderations"
        data = {
            "input": messages,
            "model": model,
        }
    elif "embedding" in model:
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

    elif  "gpt-4" in model or "vision" in model or "glm-4v" in model or "glm-4v-plus" in model or "claude-3" in model or "gemini-1.5" in model or "gemini-2.0" in model or "gemini-exp" in model or "learnlm-1.5-pro-experimental" in model or "o1" in model:
        if image_base64:
                api_url += "/v1/chat/completions"
                data = {
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": messages},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                                },
                            ],
                        }
                    ],
                    "model": model,
                    "max_tokens": int(max_tokens),
                    "stream": True,
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
    elif "o1" in model and "all" not in model:
        api_url += "/v1/chat/completions"
        data = {
                    "messages": json.loads(messages),
                    "model": model,
                    "max_tokens": int(max_tokens),
                    "temperature": 1,
                    "top_p": 1,
                    "n": 1,
                    "stream": True,

            }

    elif "deepseek-r" in model:
        api_url += "/v1/chat/completions"
        data = {
                    "messages": json.loads(messages),
                    "model": model,
                    "max_tokens": int(max_tokens),
                    "n": 1,
                    "stream": False,

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


    # Ensure data is not None before making the request
    if data is None:
        return jsonify({"error": {"message": "Unable to process the request.", "type": "data_error", "code": ""}})

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
                    "仇恨/威胁性": result["categories"]["hate/threatening"],
                    "骚扰": result["categories"]["harassment"],
                    "骚扰/威胁性": result["categories"]["harassment/threatening"],
                    "自残": result["categories"]["self-harm"],
                    "自残/意图": result["categories"]["self-harm/intent"],
                    "自残/说明": result["categories"]["self-harm/instructions"],
                    "性内容": result["categories"]["sexual"],
                    "性内容/未成年": result["categories"]["sexual/minors"],
                    "暴力": result["categories"]["violence"],
                    "暴力/图文": result["categories"]["violence/graphic"]
                },
                "违规类别分数(越大置信度越高)": {
                    "仇恨分数": result["category_scores"]["hate"],
                    "仇恨分数/威胁性": result["category_scores"]["hate/threatening"],
                    "骚扰分数": result["category_scores"]["harassment"],
                    "骚扰分数/威胁性": result["category_scores"]["harassment/threatening"],
                    "自残分数": result["category_scores"]["self-harm"],
                    "自残分数/意图": result["category_scores"]["self-harm/intent"],
                    "自残分数/说明": result["category_scores"]["self-harm/instructions"],
                    "性内容分数": result["category_scores"]["sexual"],
                    "性内容分数/未成年": result["category_scores"]["sexual/minors"],
                    "暴力分数": result["category_scores"]["violence"],
                    "暴力分数/图文": result["category_scores"]["violence/graphic"]
                },
            }
            result_list.append(result_data)

        # 返回包含所有结果的列表，并将其转换为可读的字符串
        return json.dumps(result_list, ensure_ascii=False)
    # text-moderation，接收审查结果
    if "omni-moderation" in model:
        response_data = json.loads(resp.content.decode('utf-8'))
        moderation_results = response_data["results"]

        # 提取每个结果的内容并按顺序存储在列表中
        result_list = []
        for result in moderation_results:
            result_data = {
                "有害标记": result["flagged"],
                "违规类别": {
                    "非法": result["categories"]["illicit"],
                    "非法/暴力": result["categories"]["illicit/violent"],
                    "仇恨": result["categories"]["hate"],
                    "仇恨/威胁性": result["categories"]["hate/threatening"],
                    "骚扰": result["categories"]["harassment"],
                    "骚扰/威胁性": result["categories"]["harassment/threatening"],
                    "自残": result["categories"]["self-harm"],
                    "自残/意图": result["categories"]["self-harm/intent"],
                    "自残/说明": result["categories"]["self-harm/instructions"],
                    "性内容": result["categories"]["sexual"],
                    "性内容/未成年": result["categories"]["sexual/minors"],
                    "暴力": result["categories"]["violence"],
                    "暴力/图文": result["categories"]["violence/graphic"]
                },
                "违规类别分数(越大置信度越高)": {
                    "非法": result["category_scores"]["illicit"],
                    "非法/暴力": result["category_scores"]["illicit/violent"],
                    "仇恨分数": result["category_scores"]["hate"],
                    "仇恨分数/威胁性": result["category_scores"]["hate/threatening"],
                    "骚扰分数": result["category_scores"]["harassment"],
                    "骚扰分数/威胁性": result["category_scores"]["harassment/threatening"],
                    "自残分数": result["category_scores"]["self-harm"],
                    "自残分数/意图": result["category_scores"]["self-harm/intent"],
                    "自残分数/说明": result["category_scores"]["self-harm/instructions"],
                    "性内容分数": result["category_scores"]["sexual"],
                    "性内容分数/未成年": result["category_scores"]["sexual/minors"],
                    "暴力分数": result["category_scores"]["violence"],
                    "暴力分数/图文": result["category_scores"]["violence/graphic"]
                },
            }
            result_list.append(result_data)

        # 返回包含所有结果的列表，并将其转换为可读的字符串
        return json.dumps(result_list, ensure_ascii=False)

    # text-embedding，接收多维数组
    if "embedding" in model:
        response_data = json.loads(resp.content.decode('utf-8'))
        embedding = response_data["data"][0]["embedding"]
        return jsonify(embedding)

    # 在TTS模型的情况下，返回base64编码的音频数据
    if "tts-1" in model:
        # 解析响应的音频数据并进行base64编码
        audio_data = base64.b64encode(resp.content).decode('utf-8')
        return jsonify(audio_data)
        
    # gpt模型回复接收
    def generate():
        errorStr = ""
        respStr = ""
        for chunk in resp.iter_lines():
            if chunk:
                streamStr = chunk.decode("utf-8").replace("data: ", "")
                try:
                    streamStr = streamStr.strip("[DONE]")
                    streamDict = json.loads(streamStr)
                except json.JSONDecodeError:
                    errorStr += streamStr.strip()
                    continue

                if "choices" in streamDict:
                    if streamDict["choices"]:
                        delData = streamDict["choices"][0]
                        if streamDict.get("model") is None:
                            break
                        else:
                            if "text" in delData:
                                respStr = delData["text"]
                                yield respStr
                            elif "delta" in delData and "content" in delData["delta"] and "reasoning_content" not in delData["delta"]:
                                respStr = delData["delta"]["content"]
                                yield respStr
                            elif "delta" in delData and "content" in delData["delta"] and "reasoning_content" in delData["delta"]:
                                respStr = delData["delta"]["reasoning_content"] + delData["delta"]["content"]
                                yield respStr
                            elif "message" in delData and "content" in delData["message"] and "reasoning_content" not in delData["message"]:
                                respStr = delData["message"]["content"]
                                yield respStr
                            elif "message" in delData and "content" in delData["message"] and "reasoning_content" in delData["message"]:
                                respStr = delData["message"]["reasoning_content"] + delData["message"]["content"]
                                yield respStr
                    else:
                        errorStr += f"Empty choices in data: {streamDict}\n"
                else:
                    errorStr += f"Unexpected data format: {streamDict}\n"

        if not respStr and errorStr:
            with app.app_context():
                yield errorStr

    return Response(generate(), content_type='application/octet-stream')

if __name__ == '__main__':
    app.run('0.0.0.0', 80)
