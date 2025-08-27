# -*- coding: utf-8 -*-

# 导入必要的库
from datetime import datetime, timedelta  # 用于处理日期和时间
from flask import Flask, request, jsonify, render_template, Response  # Flask框架相关组件
import requests  # 用于发送HTTP请求
import json  # 用于处理JSON数据
import os  # 用于与操作系统交互，如文件路径操作
import random  # 用于生成随机数，如此处用于随机选择API Key
import base64  # 用于Base64编码，如此处用于处理TTS音频数据

# 初始化Flask应用
app = Flask(__name__)

# 从配置文件 settings.py 加载应用配置
app.config.from_pyfile('settings.py')


@app.route("/", methods=["GET"])
def index():
    """
    根路由，用于渲染并返回前端的主聊天页面 (chat.html)。
    """
    return render_template("chat.html")


@app.route("/models", methods=["GET"])
def get_models():
    """
    获取可用模型列表的API端点。
    它会根据前端提供的apiKey和api_url，或者使用服务器的默认配置，
    向目标API的 /v1/models 发送请求。
    """
    # 从前端的查询参数中获取apiKey和api_url
    api_key = request.args.get("apiKey", None)
    api_url = request.args.get("api_url", None)

    # 如果前端没有提供api_url，则使用服务器配置的默认URL
    if not api_url:
        api_url = app.config.get("API_URL1", None)

    # 如果前端没有提供apiKey，则从服务器配置的默认密钥池中随机选择一个
    if not api_key:
        api_keys = app.config.get("API_KEYS1", [])
        if not api_keys:
            # 如果服务器也没有配置默认密钥，返回配置错误
            return jsonify({"error": {"message": "服务器未配置默认API密钥。", "type": "config_error"}}), 500
        api_key = random.choice(api_keys)

    # 确保最终有可用的apiKey和api_url
    if not api_key or not api_url:
        return jsonify({"error": {"message": "缺少API密钥或URL。", "type": "config_error"}}), 400

    # 构造请求头
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # 拼接最终的请求URL
    models_url = f"{api_url.rstrip('/')}/v1/models"

    try:
        # 发送GET请求获取模型列表
        resp = requests.get(models_url, headers=headers, timeout=15)
        resp.raise_for_status()  # 如果请求失败 (状态码 4xx 或 5xx)，则抛出异常
        models_data = resp.json()

        # 如果返回的数据中包含'data'字段且为列表，则按模型ID字母顺序排序
        if 'data' in models_data and isinstance(models_data['data'], list):
            models_data['data'] = sorted(models_data['data'], key=lambda x: x.get('id', ''))

        return jsonify(models_data)

    except requests.exceptions.RequestException as e:
        # 捕获并处理网络或API请求相关的异常
        return jsonify({"error": {"message": f"从API获取模型失败: {str(e)}", "type": "api_error"}}), 500
    except Exception as e:
        # 捕获其他未知异常
        return jsonify({"error": {"message": f"发生意外错误: {str(e)}", "type": "internal_error"}}), 500


@app.route("/default_balance", methods=["GET"])
def get_balance():
    """
    获取API密钥余额信息的API端点。
    同样，它会优先使用前端提供的配置，否则回退到服务器的默认配置。
    """
    # 从前端请求中获取用户指定的apiKey和apiUrl
    user_api_key = request.args.get("apiKey", None)
    user_api_url = request.args.get("api_url", None)

    # --- 智能回退逻辑 ---
    # 如果用户提供了apiKey，则使用用户的；否则，从服务器默认密钥池中随机选择一个
    if user_api_key:
        final_api_key = user_api_key
    else:
        api_keys = app.config.get("API_KEYS1", [])
        if not api_keys:
            return jsonify({"error": {"message": "未设置默认的 API 密钥", "type": "config_error"}}), 500
        final_api_key = random.choice(api_keys)

    # 如果用户提供了api_url，则使用用户的；否则，使用服务器的默认URL
    if user_api_url:
        final_api_url = user_api_url
    else:
        final_api_url = app.config.get("API_URL1", None)
    # --- 智能回退逻辑结束 ---

    # 检查最终配置是否齐全
    if not final_api_key or not final_api_url:
        return jsonify({"error": {"message": "未配置 API 密钥或 URL", "type": "config_error"}})

    # 构造请求头
    headers = {
        "Authorization": f"Bearer {final_api_key}",
        "Content-Type": "application/json"
    }

    try:
        # 获取订阅信息，从中得到总额度
        subscription_url = f"{final_api_url.rstrip('/')}/v1/dashboard/billing/subscription"
        subscription_resp = requests.get(subscription_url, headers=headers, timeout=10)
        subscription_resp.raise_for_status()
        subscription_data = subscription_resp.json()
        total = subscription_data.get('hard_limit_usd', 0)

        # 获取近99天的使用量信息
        start_date = datetime.now() - timedelta(days=99)
        end_date = datetime.now()
        usage_url = f"{final_api_url.rstrip('/')}/v1/dashboard/billing/usage?start_date={start_date.strftime('%Y-%m-%d')}&end_date={end_date.strftime('%Y-%m-%d')}"
        usage_resp = requests.get(usage_url, headers=headers, timeout=10)
        usage_resp.raise_for_status()
        usage_data = usage_resp.json()
        total_usage = usage_data.get('total_usage', 0) / 100  # 使用量单位是美分，需转换为美元
        remaining = total - total_usage

        # 返回格式化的余额信息
        return jsonify({
            "total_balance": total,
            "used_balance": total_usage,
            "remaining_balance": remaining
        })
    except requests.exceptions.RequestException as e:
        # 处理API请求错误
        return jsonify({"error": {"message": f"API 错误：{str(e)}", "type": "api_error"}})
    except Exception as e:
        # 处理其他服务器内部错误
        return jsonify({"error": {"message": f"服务器错误：{str(e)}", "type": "server_error"}})


@app.route("/chat", methods=["POST"])
def chat():
    """
    处理聊天、绘图、文本审核等请求的核心API端点。
    """
    # 从POST表单中获取各项参数
    messages = request.form.get("prompts", None)
    apiKey = request.form.get("apiKey", None)
    model = request.form.get("model", "gpt-5")
    temperature = request.form.get("temperature", 0.5)
    max_tokens = request.form.get("max_tokens", 4000)
    password = request.form.get("password", None)
    api_url = request.form.get("api_url", None)
    image_base64 = request.form.get("image_base64", None) # 用于多模态视觉模型

    # --- 日志记录 ---
    # 获取当前时间和日期
    current_time = datetime.now().strftime("%Y年%m月%d日%H:%M:%S")
    current_date = datetime.now().strftime("%Y.%m.%d")
    # 构建日志文件路径
    current_directory = os.path.dirname(os.path.realpath(__file__))
    folder_path = os.path.join(current_directory, "对话记录")
    # 如果日志文件夹不存在，则创建
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    # 将请求信息追加写入到当天的日志文件中
    file_name = f"{current_date}.txt"
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, "a", encoding="utf-8") as all_info_file:
        all_info_file.write(
            f"Time: {current_time}\nModel: {model}\nApiKey: {apiKey}\nApi_url: {api_url}\nMessage: {messages}\n\n")

    # --- API密钥和URL选择逻辑 ---
    # 如果用户未提供api_url，使用服务器默认配置
    if api_url is None:
        api_url = app.config.get("API_URL", None)

    # 定义需要密码验证的高级模型关键字列表
    premium_models_keywords = ["gpt-4", "gpt-5", "dall", "claude", "SparkDesk", "gemini", "o1", "o3", "grok",
                               "o4", "chatgpt", "embedding", "moderation", "glm", "yi", "commmand", "stable",
                               "deep", "midjourney", "douubao", "qwen", "co", "suno", "abab", "chat"]

    # 检查当前模型是否是高级模型
    is_premium_model = any(keyword in model for keyword in premium_models_keywords)

    # 如果用户未提供apiKey
    if apiKey is None:
        # 如果不是高级模型，则使用默认的免费密钥池
        if not is_premium_model:
            api_keys = app.config.get("API_KEYS", [])
            apiKey = os.environ.get('OPENAI_API_KEY', random.choice(api_keys))
        # 如果是高级模型
        else:
            # 检查是否提供了密码
            if not password:
                return jsonify({"error": {"message": "请联系群主获取授权码或者输入自己的apikey！！！",
                                          "type": "empty_password_error", "code": ""}})
            # 验证密码是否有效
            valid_passwords = ["freegpt", "D2f9A7c5", "3E6bR8s1", "H4j7N9q2", "5T6gY1h9", "L8m3W7e2"]
            if password not in valid_passwords:
                return jsonify({"error": {"message": "请检查并输入正确的授权码或者输入自己的apikey！！！",
                                          "type": "invalid_password_error", "code": ""}})
            
            # 根据不同的密码，选择对应的API密钥池和URL
            if password == "freegpt":
                api_keys = app.config.get("API_KEYS1", [])
                apiKey = random.choice(api_keys)
                api_url = app.config.get("API_URL1", None)
            elif password == "D2f9A7c5":
                api_keys = app.config.get("API_KEYS2", [])
                apiKey = random.choice(api_keys)
                api_url = app.config.get("API_URL2", None)
            elif password == "3E6bR8s1":
                api_keys = app.config.get("API_KEYS3", [])
                apiKey = random.choice(api_keys)
                api_url = app.config.get("API_URL3", None)
            elif password == "H4j7N9q2":
                api_keys = app.config.get("API_KEYS4", [])
                apiKey = random.choice(api_keys)
                api_url = app.config.get("API_URL4", None)
            elif password == "5T6gY1h9":
                api_keys = app.config.get("API_KEYS5", [])
                apiKey = random.choice(api_keys)
                api_url = app.config.get("API_URL5", None)
            elif password == "L8m3W7e2":
                api_keys = app.config.get("API_KEYS6", [])
                apiKey = random.choice(api_keys)
                api_url = app.config.get("API_URL6", None)

    # 针对gizmo模型的特殊处理 (如果API key仍然为空且密码不是已知密码)
    if apiKey is None:
        valid_passwords = ["freegpt", "D2f9A7c5", "3E6bR8s1", "H4j7N9q2", "5T6gY1h9", "L8m3W7e2"]
        if password not in valid_passwords:
            if "gizmo" in model:
                api_keys = app.config.get("API_KEYS7", [])
                apiKey = random.choice(api_keys)
                api_url = app.config.get("API_URL7", None)

    # --- 根据模型类型构建请求体(data)和URL ---
    data = None # 初始化data变量
    
    # 绘图模型
    if "dall-e" in model or "cogview" in model:
        api_url += "/v1/images/generations"
        # 根据不同的dall-e模型变体设置不同的参数
        if model == "dall-e-2":
            data = {"model": "dall-e-2", "prompt": messages, "n": 1, "size": "256x256"}
        elif model == "dall-e-2-m":
            data = {"model": "dall-e-2", "prompt": messages, "n": 1, "size": "512x512"}
        elif model == "dall-e-2-l":
            data = {"model": "dall-e-2", "prompt": messages, "n": 1, "size": "1024x1024"}
        elif model == "dall-e-3":
            data = {"model": "dall-e-3", "prompt": messages, "n": 1, "size": "1024x1024", "quality": "standard", "style": "natural"}
        elif model == "dall-e-3-w":
            data = {"model": "dall-e-3", "prompt": messages, "n": 1, "size": "1792x1024", "quality": "standard", "style": "natural"}
        elif model == "dall-e-3-l":
            data = {"model": "dall-e-3", "prompt": messages, "n": 1, "size": "1024x1792", "quality": "standard", "style": "natural"}
        elif model == "dall-e-3-hd":
            data = {"model": "dall-e-3", "prompt": messages, "n": 1, "size": "1024x1024", "quality": "hd", "style": "natural"}
        elif model == "dall-e-3-w-hd":
            data = {"model": "dall-e-3", "prompt": messages, "n": 1, "size": "1792x1024", "quality": "hd", "style": "natural"}
        elif model == "dall-e-3-l-hd":
            data = {"model": "dall-e-3", "prompt": messages, "n": 1, "size": "1024x1792", "quality": "hd", "style": "natural"}
        elif model == "dall-e-3-v":
            data = {"model": "dall-e-3", "prompt": messages, "n": 1, "size": "1024x1024", "quality": "standard", "style": "vivid"}
        elif model == "dall-e-3-w-v":
            data = {"model": "dall-e-3", "prompt": messages, "n": 1, "size": "1792x1024", "quality": "standard", "style": "vivid"}
        elif model == "dall-e-3-l-v":
            data = {"model": "dall-e-3", "prompt": messages, "n": 1, "size": "1024x1792", "quality": "standard", "style": "vivid"}
        elif model == "dall-e-3-p":
            data = {"model": "dall-e-3", "prompt": messages, "n": 1, "size": "1024x1024", "quality": "hd", "style": "vivid"}
        elif model == "dall-e-3-w-p":
            data = {"model": "dall-e-3", "prompt": messages, "n": 1, "size": "1792x1024", "quality": "hd", "style": "vivid"}
        elif model == "dall-e-3-l-p":
            data = {"model": "dall-e-3", "prompt": messages, "n": 1, "size": "1024x1792", "quality": "hd", "style": "vivid"}
        elif model == "cogview-3":
            data = {"model": "cogview-3", "prompt": messages, "size": "1024x1024"}
        elif model == "cogview-3-plus":
            data = {"model": "cogview-3-plus", "prompt": messages, "size": "1024x1024"}
    
    # 文本审核模型
    elif "moderation" in model:
        api_url += "/v1/moderations"
        data = {"input": messages, "model": model}
    
    # 文本嵌入模型
    elif "embedding" in model:
        api_url += "/v1/embeddings"
        data = {"input": messages, "model": model}
    
    # 文本转语音 (TTS) 模型
    elif "tts" in model:
        api_url += "/v1/audio/speech"
        # 清理messages中可能存在的JSON结构残留
        clean_messages = messages.replace("user", "").replace("content", "").replace("role", "").replace("assistant", "")
        data = {"input": clean_messages, "model": model, "voice": "alloy"}

    # 旧版的补全模型 (Completions API)
    elif "gpt-3.5-turbo-instruct" in model or "babbage-002" in model or "davinci-002" in model:
        api_url += "/v1/completions"
        data = {
            "prompt": messages,
            "model": model,
            "max_tokens": int(max_tokens),
            "temperature": float(temperature),
            "stream": True,
        }
    
    # 视觉或高级对话模型 (Chat Completions API)
    elif any(keyword in model for keyword in ["gpt-4", "gpt-5", "vision", "glm-4v", "claude", "gemini", "o1", "o3", "o4"]):
        api_url += "/v1/chat/completions"
        # 如果有图像数据，则构建多模态消息体
        if image_base64:
            data = {
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": messages},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}},
                    ],
                }],
                "model": model,
                "max_tokens": int(max_tokens),
                "stream": True,
            }
        # 否则，构建标准文本消息体
        else:
            data = {
                "messages": json.loads(messages),
                "model": model,
                "max_tokens": int(max_tokens),
                "temperature": float(temperature),
                "stream": True,
            }
            # 对特定模型族应用不同的默认参数
            if any(keyword in model for keyword in ["claude", "o1", "o3", "o4", "gpt-5"]):
                data["temperature"] = 1.0
                data.pop("top_p", None)  # 移除top_p，如果存在的话
                
    # 其他所有对话模型 (默认使用Chat Completions API)
    else:
        api_url += "/v1/chat/completions"
        data = {
            "messages": json.loads(messages),
            "model": model,
            "max_tokens": int(max_tokens),
            "temperature": float(temperature),
            "stream": True,
        }

    # 如果data未被正确构建，返回错误
    if data is None:
        return jsonify({"error": {"message": "无法根据模型处理请求。", "type": "data_error", "code": ""}})

    # --- 发送请求到API ---
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {apiKey}",
    }

    try:
        # 使用流式传输(stream=True)发送POST请求，设置较长的超时时间
        resp = requests.post(url=api_url, headers=headers, json=data, stream=True, timeout=(120, 120))
    except requests.exceptions.Timeout:
        return jsonify({"error": {"message": "请求超时", "type": "timeout_error", "code": ""}})
    except Exception as e:
        return jsonify({"error": {"message": f"发生未知错误：{str(e)}", "type": "unexpected_error", "code": ""}})

    # --- 根据模型类型处理响应 ---

    # 如果是绘图模型，直接返回图片URL
    if "dall-e" in model or "cogview" in model:
        response_data = resp.json()
        image_url = response_data["data"][0]["url"]
        return jsonify(image_url)

    # 如果是文本审核模型，格式化并返回审核结果
    if "moderation" in model:
        response_data = resp.json()
        result_list = []
        for result in response_data.get("results", []):
            # 将API返回的英文分类和布尔值转换为更易读的中文描述
            categories = result.get("categories", {})
            category_scores = result.get("category_scores", {})
            result_data = {
                "有害标记": result.get("flagged"),
                "违规类别": {k: "是" if v else "否" for k, v in categories.items()},
                "违规类别置信度": category_scores
            }
            result_list.append(result_data)
        # 使用json.dumps以保证中文字符正确显示
        return Response(json.dumps(result_list, ensure_ascii=False, indent=2), content_type="application/json; charset=utf-8")
        
    # 如果是嵌入模型，返回嵌入向量
    if "embedding" in model:
        response_data = resp.json()
        embedding = response_data["data"][0]["embedding"]
        return jsonify(embedding)

    # 如果是TTS模型，返回Base64编码的音频数据
    if "tts" in model:
        audio_data = base64.b64encode(resp.content).decode('utf-8')
        return jsonify(audio_data)

    # 如果是流式对话模型，使用生成器函数逐步返回内容
    def generate():
        error_str = ""
        has_yielded = False
        for chunk in resp.iter_lines():
            if not chunk:
                continue
            
            stream_str = chunk.decode("utf-8").replace("data: ", "")
            if stream_str.strip() == "[DONE]":
                break

            try:
                stream_dict = json.loads(stream_str)
                
                if "choices" in stream_dict and stream_dict["choices"]:
                    delta_data = stream_dict["choices"][0].get("delta", {})
                    if "content" in delta_data and delta_data["content"] is not None:
                        content_chunk = delta_data["content"]
                        yield content_chunk
                        has_yielded = True
                # 兼容一些非OpenAI标准但类似的流式格式
                elif "message" in stream_dict and "content" in stream_dict["message"]:
                    content_chunk = stream_dict["message"]["content"]
                    yield content_chunk
                    has_yielded = True

            except json.JSONDecodeError:
                # 累积无法解析的字符串，可能是错误信息
                error_str += stream_str
            except Exception:
                # 捕获解析流数据时可能出现的其他错误
                error_str += f"流数据解析错误: {stream_str}"
        
        # 如果整个流都没有产生任何内容，且累积了错误信息，则返回错误
        if not has_yielded and error_str:
            yield f"API错误或响应格式不兼容: {error_str}"

    return Response(generate(), content_type='application/octet-stream')

if __name__ == '__main__':
    # 启动Flask应用，监听在所有网络接口的80端口上
    app.run('0.0.0.0', 80)
