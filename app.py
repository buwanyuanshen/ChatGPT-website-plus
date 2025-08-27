# -*- coding: utf-8 -*-
# 导入所需的库
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, Response
import requests
import json
import os
import random
import base64

# 初始化 Flask 应用
app = Flask(__name__)

# 从 settings.py 配置文件中加载配置
app.config.from_pyfile('settings.py')


# 定义根路由，用于显示聊天页面
@app.route("/", methods=["GET"])
def index():
    """渲染并返回主聊天页面 chat.html"""
    return render_template("chat.html")

# 定义/models路由，用于获取可用的模型列表
@app.route("/models", methods=["GET"])
def get_models():
    """
    从目标API获取模型列表。
    它会优先使用前端传递的apiKey和api_url。
    如果前端未提供，则会从服务器配置中随机选择一个备用。
    """
    # 从前端的查询参数中获取apiKey和api_url
    apiKey = request.args.get("apiKey", None)
    api_url = request.args.get("api_url", None)

    # 如果前端没有提供api_url，则使用服务器配置中的默认URL
    if not api_url:
        api_url = app.config.get("API_URL1", None)

    # 如果前端没有提供apiKey，则从服务器配置的密钥池中随机选择一个
    if not apiKey:
        api_keys = app.config.get("API_KEYS1", [])
        if not api_keys:
             return jsonify({"error": {"message": "服务器没有配置默认的API密钥。", "type": "config_error"}}), 500
        apiKey = random.choice(api_keys)

    # 确保最终有可用的apiKey和api_url
    if not apiKey or not api_url:
        return jsonify({"error": {"message": "缺少API密钥或URL。", "type": "config_error"}}), 400

    # 设置请求头，包含认证信息
    headers = {
        "Authorization": f"Bearer {apiKey}",
        "Content-Type": "application/json"
    }
    
    # 构造获取模型的完整URL
    models_url = f"{api_url.rstrip('/')}/v1/models"

    try:
        # 发送GET请求获取模型列表
        resp = requests.get(models_url, headers=headers, timeout=15)
        resp.raise_for_status()  # 如果请求失败（状态码4xx或5xx），则抛出异常
        models_data = resp.json()
        
        # 如果返回数据中包含'data'列表，则按模型ID字母顺序排序
        if 'data' in models_data and isinstance(models_data['data'], list):
            models_data['data'] = sorted(models_data['data'], key=lambda x: x.get('id', ''))
            
        return jsonify(models_data)
        
    except requests.exceptions.RequestException as e:
        # 处理网络或API请求相关的错误
        return jsonify({"error": {"message": f"从API获取模型失败: {str(e)}", "type": "api_error"}}), 500
    except Exception as e:
        # 处理其他意外错误
        return jsonify({"error": {"message": f"发生意外错误: {str(e)}", "type": "internal_error"}}), 500
        
# 定义/default_balance路由，用于查询API密钥的余额信息
@app.route("/default_balance", methods=["GET"])
def get_balance():
    """
    查询指定API密钥的余额信息。
    优先使用前端提供的apiKey和api_url，若未提供则使用服务器的默认配置。
    """
    # 从前端请求中获取用户指定的apiKey和api_url
    user_api_key = request.args.get("apiKey", None)
    user_api_url = request.args.get("api_url", None)

    # --- 智能回退逻辑 ---
    # 如果用户提供了apiKey，则使用用户的；否则从服务器配置中随机选择一个
    if user_api_key:
        final_api_key = user_api_key
    else:
        api_keys = app.config.get("API_KEYS1", [])
        if not api_keys:
             return jsonify({"error": {"message": "未设置默认的 API 密钥", "type": "config_error"}}), 500
        final_api_key = random.choice(api_keys)

    # 如果用户提供了api_url，则使用用户的；否则使用服务器配置的默认URL
    if user_api_url:
        final_api_url = user_api_url
    else:
        final_api_url = app.config.get("API_URL1", None)
    # --- 智能回退逻辑结束 ---

    # 检查最终的apiKey和api_url是否存在
    if not final_api_key or not final_api_url:
        return jsonify({"error": {"message": "未配置 API 密钥或 URL", "type": "config_error"}})

    # 设置请求头
    headers = {
        "Authorization": f"Bearer {final_api_key}",
        "Content-Type": "application/json"
    }

    try:
        # 构建查询订阅信息的URL并发送请求
        subscription_url = f"{final_api_url.rstrip('/')}/v1/dashboard/billing/subscription"
        subscription_resp = requests.get(subscription_url, headers=headers, timeout=10)
        subscription_resp.raise_for_status()
        subscription_data = subscription_resp.json()
        total = subscription_data.get('hard_limit_usd', 0)

        # 构建查询使用量的URL并发送请求（查询过去99天）
        start_date = datetime.now() - timedelta(days=99)
        end_date = datetime.now()
        usage_url = f"{final_api_url.rstrip('/')}/v1/dashboard/billing/usage?start_date={start_date.strftime('%Y-%m-%d')}&end_date={end_date.strftime('%Y-%m-%d')}"
        usage_resp = requests.get(usage_url, headers=headers, timeout=10)
        usage_resp.raise_for_status()
        usage_data = usage_resp.json()
        total_usage = usage_data.get('total_usage', 0) / 100  # 使用量单位为美分，需转换为美元
        remaining = total - total_usage

        # 返回包含总额度、已使用、剩余额度的JSON数据
        return jsonify({
            "total_balance": total,
            "used_balance": total_usage,
            "remaining_balance": remaining
        })
    except requests.exceptions.RequestException as e:
        # 处理API请求相关的错误
        return jsonify({"error": {"message": f"API 错误：{str(e)}", "type": "api_error"}})
    except Exception as e:
        # 处理其他服务器内部错误
        return jsonify({"error": {"message": f"服务器错误：{str(e)}", "type": "server_error"}})


# 定义/chat路由，处理聊天请求
@app.route("/chat", methods=["POST"])
def chat():
    """
    处理核心的聊天、绘图、语音合成等请求。
    该函数逻辑复杂，主要分为几大块：
    1. 获取前端参数。
    2. 将请求信息记录到本地日志文件。
    3. 根据模型名称和密码，动态选择并分配API Key和API URL。
    4. 根据不同的模型，构造符合其API要求的请求体（payload）。
    5. 发送请求到目标API。
    6. 根据模型类型，处理并返回相应格式的响应（如流式文本、图片URL、音频数据等）。
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
    current_time = datetime.now().strftime("%Y年%m月%d日%H:%M:%S")
    current_date = datetime.now().strftime("%Y.%m.%d")
    current_directory = os.path.dirname(os.path.realpath(__file__))
    folder_path = os.path.join(current_directory, "对话记录")

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    file_name = f"{current_date}.txt"
    file_path = os.path.join(folder_path, file_name)

    # 将请求的关键信息追加写入当天的日志文件
    with open(file_path, "a", encoding="utf-8") as all_info_file:
        all_info_file.write(f"Time: {current_time}\nModel: {model}\nApiKey: {apiKey}\nApi_url: {api_url}\nMessage: {messages}\n\n")

    # --- API Key 和 URL 的动态选择逻辑 ---
    # 如果前端未提供api_url，则使用配置中的默认值
    if api_url is None:
        api_url = app.config.get("API_URL", None)

    # 如果前端未提供apiKey，则根据模型名称决定是否使用免费的key池
    if apiKey is None:
        # 定义一个长列表，判断模型是否为"普通"模型
        is_premium_model = "gpt-4" in model or "gpt-5" in model or "dall" in model or "claude" in model or \
                           "SparkDesk" in model or "gemini" in model or "o1" in model or "o3" in model or \
                           "grok" in model or "o4" in model or "chatgpt" in model or "embedding" in model or \
                           "moderation" in model or "glm" in model or "yi" in model or "commmand" in model or \
                           "stable" in model or "deep" in model or "midjourney" in model or "douubao" in model or \
                           "qwen" in model or "co" in model or "suno" in model or "abab" in model or "chat" in model
        
        # 如果不是高级模型，则从默认的key池中随机选择
        if not is_premium_model:
            api_keys = app.config.get("API_KEYS", [])
            apiKey = os.environ.get('OPENAI_API_KEY', random.choice(api_keys))

    # 针对需要密码验证的高级模型进行处理
    if apiKey is None:
        is_premium_model = "gpt-4" in model or "gpt-5" in model or "dall" in model or "claude" in model or \
                           "SparkDesk" in model or "gemini" in model or "o1" in model or "o3" in model or \
                           "o4" in model or "grok" in model or "chatgpt" in model or "embedding" in model or \
                           "moderation" in model or "glm" in model or "yi" in model or "commmand" in model or \
                           "stable" in model or "deep" in model or "midjourney" in model or "douubao" in model or \
                           "qwen" in model or "co" in model or "suno" in model or "abab" in model or "chat" in model
        
        if is_premium_model:
            # 如果需要密码但未提供，返回错误
            if not password:
                return jsonify({"error": {"message": "请联系群主获取授权码或者输入自己的apikey！！！",
                                          "type": "empty_password_error", "code": ""}})
            # 如果密码不正确，返回错误
            valid_passwords = ["freegpt", "D2f9A7c5", "3E6bR8s1", "H4j7N9q2", "5T6gY1h9", "L8m3W7e2"]
            if password not in valid_passwords:
                return jsonify({
                    "error": {
                        "message": "请检查并输入正确的授权码或者输入自己的apikey！！！",
                        "type": "invalid_password_error",
                        "code": ""
                    }
                })

    # 根据正确的密码，分配对应的API Key池和API URL
    if apiKey is None:
        password_map = {
            "freegpt": ("API_KEYS1", "API_URL1"),
            "D2f9A7c5": ("API_KEYS2", "API_URL2"),
            "3E6bR8s1": ("API_KEYS3", "API_URL3"),
            "H4j7N9q2": ("API_KEYS4", "API_URL4"),
            "5T6gY1h9": ("API_KEYS5", "API_URL5"),
            "L8m3W7e2": ("API_KEYS6", "API_URL6"),
        }
        if password in password_map:
            keys_config, url_config = password_map[password]
            api_keys = app.config.get(keys_config, [])
            apiKey = os.environ.get('OPENAI_API_KEY', random.choice(api_keys))
            api_url = app.config.get(url_config, None)

    # 为gizmo模型设置专用的API Key和URL（在密码不匹配上述情况时）
    if apiKey is None:
        if "gizmo" in model and password not in ["freegpt", "D2f9A7c5", "3E6bR8s1", "H4j7N9q2", "5T6gY1h9", "L8m3W7e2"]:
            api_keys = app.config.get("API_KEYS7", [])
            apiKey = os.environ.get('OPENAI_API_KEY', random.choice(api_keys))
            api_url = app.config.get("API_URL7", None)

    # --- 根据模型名称构建不同的请求体（data） ---
    data = None
    if "dall-e" in model:
        api_url += "/v1/images/generations"
        size_map = {
            "dall-e-2": "256x256", "dall-e-2-m": "512x512", "dall-e-2-l": "1024x1024",
            "dall-e-3": "1024x1024", "dall-e-3-hd": "1024x1024", "dall-e-3-v": "1024x1024", "dall-e-3-p": "1024x1024",
            "dall-e-3-w": "1792x1024", "dall-e-3-w-hd": "1792x1024", "dall-e-3-w-v": "1792x1024", "dall-e-3-w-p": "1792x1024",
            "dall-e-3-l": "1024x1792", "dall-e-3-l-hd": "1024x1792", "dall-e-3-l-v": "1024x1792", "dall-e-3-l-p": "1024x1792",
        }
        quality_map = {"hd": "hd", "p": "hd"}
        style_map = {"v": "vivid", "p": "vivid"}
        
        data = {
            "model": "dall-e-3" if "dall-e-3" in model else "dall-e-2",
            "prompt": messages,
            "n": 1,
            "size": size_map.get(model, "1024x1024"),
            "quality": quality_map.get(model.split('-')[-1], "standard"),
            "style": style_map.get(model.split('-')[-1], "natural"),
        }
    elif model in ["cogview-3", "cogview-3-plus"]:
        api_url += "/v1/images/generations"
        data = {"model": model, "prompt": messages, "size": "1024x1024"}
    elif "moderation" in model:
        api_url += "/v1/moderations"
        data = {"input": messages, "model": model}
    elif "embedding" in model:
        api_url += "/v1/embeddings"
        data = {"input": messages, "model": model}
    elif "tts" in model:
        api_url += "/v1/audio/speech"
        # 清理messages中可能存在的JSON结构残留，只保留纯文本
        clean_messages = messages.replace("user", "").replace("content", "").replace("role", "").replace("assistant", "")
        data = {"input": clean_messages, "model": model, "voice": "alloy"}
    elif model in ["gpt-3.5-turbo-instruct", "babbage-002", "davinci-002"]:
        api_url += "/v1/completions"
        data = {
            "prompt": messages, "model": model, "max_tokens": int(max_tokens),
            "temperature": float(temperature), "top_p": 1, "n": 1, "stream": True,
        }
    else:  # 默认处理所有其他的聊天模型
        api_url += "/v1/chat/completions"
        # 检查是否为视觉模型并有图片输入
        is_vision_model = "vision" in model or "glm-4v" in model or "claude" in model or "gemini-1.5" in model or "o" in model
        if image_base64 and (is_vision_model or "gpt-4" in model):
            data = {
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": messages},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}},
                    ],
                }],
                "model": model, "max_tokens": int(max_tokens), "stream": True,
            }
        else: # 标准聊天请求
            data = {
                "messages": json.loads(messages),
                "model": model,
                "stream": True,
                "max_tokens": int(max_tokens),
                "temperature": float(temperature),
                "n": 1
            }
            # 为特定模型覆盖或设置特定参数
            if "claude-3" in model or "claude-4" in model or "claude-sonnet" in model or "claude-opus" in model:
                # Claude模型通常不需要top_p
                data.pop("top_p", None) 
            elif any(x in model for x in ["o1", "o3", "o4", "gpt-5"]) and "all" not in model:
                data["temperature"] = 1
                data["top_p"] = 1
            elif "grok-2-image" in model:
                data.pop("max_tokens", None)
                data.pop("temperature", None)
                data.pop("stream", None)
            
            # 确保 top_p 存在于非特定模型中
            if "top_p" not in data:
                 data["top_p"] = 1

    # 如果data仍为None，说明模型不受支持，返回错误
    if data is None:
        return jsonify({"error": {"message": "无法处理该模型的请求。", "type": "data_error", "code": ""}})
    
    # --- 发送请求并处理响应 ---
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {apiKey}"}

    try:
        resp = requests.post(url=api_url, headers=headers, json=data, stream=True, timeout=(120, 120))
    except requests.exceptions.Timeout:
        return jsonify({"error": {"message": "请求超时", "type": "timeout_error", "code": ""}})
    except Exception as e:
        return jsonify({"error": {"message": f"发生未知错误：{str(e)}", "type": "unexpected_error", "code": ""}})

    # --- 根据模型类型处理不同的响应格式 ---
    # 图像生成模型：直接返回图片URL
    if "dall-e" in model or "cogview" in model:
        response_data = resp.json()
        image_url = response_data["data"][0]["url"]
        return jsonify(image_url)

    # 文本审核模型：格式化并返回审核结果
    if "moderation" in model:
        response_data = resp.json()
        result_list = []
        for result in response_data.get("results", []):
            # 将API返回的英文类别和布尔值格式化为中文，方便阅读
            categories_cn = {
                "hate": ("仇恨", result["categories"]["hate"]), "hate/threatening": ("仇恨/威胁", result["categories"]["hate/threatening"]),
                "harassment": ("骚扰", result["categories"]["harassment"]), "harassment/threatening": ("骚扰/威胁", result["categories"]["harassment/threatening"]),
                "self-harm": ("自残", result["categories"]["self-harm"]), "self-harm/intent": ("自残/意图", result["categories"]["self-harm/intent"]),
                "self-harm/instructions": ("自残/教唆", result["categories"]["self-harm/instructions"]),
                "sexual": ("色情", result["categories"]["sexual"]), "sexual/minors": ("色情/未成年", result["categories"]["sexual/minors"]),
                "violence": ("暴力", result["categories"]["violence"]), "violence/graphic": ("暴力/血腥", result["categories"]["violence/graphic"]),
            }
            if "omni" in model:
                categories_cn.update({
                    "illicit": ("非法活动", result["categories"].get("illicit")),
                    "illicit/violent": ("非法活动/暴力", result["categories"].get("illicit/violent"))
                })
            
            result_data = {
                "是否违规": "是" if result["flagged"] else "否",
                "违规类别": {k: "是" if v else "否" for k, (k, v) in categories_cn.items()},
                "各项违规置信度": result["category_scores"]
            }
            result_list.append(result_data)
        # 使用 json.dumps 美化输出，ensure_ascii=False 保证中文正常显示
        return Response(json.dumps(result_list, indent=4, ensure_ascii=False), mimetype='application/json')
    
    # 文本嵌入模型：返回嵌入向量
    if "embedding" in model:
        response_data = resp.json()
        embedding = response_data["data"][0]["embedding"]
        return jsonify(embedding)

    # 文本转语音模型：返回Base64编码的音频数据
    if "tts" in model:
        audio_data = base64.b64encode(resp.content).decode('utf-8')
        return jsonify(audio_data)

    # --- 默认处理：流式返回聊天模型的文本响应 ---
    def generate():
        """一个生成器函数，用于逐块处理和返回流式响应。"""
        errorStr = ""
        # 遍历从API返回的每一行数据
        for chunk in resp.iter_lines():
            if chunk:
                # 清理SSE（Server-Sent Events）格式的行，移除 "data: " 前缀
                streamStr = chunk.decode("utf-8").replace("data: ", "")
                if not streamStr or streamStr.strip() == "[DONE]":
                    continue # 如果是空行或结束标志，则跳过

                try:
                    # 解析JSON数据
                    streamDict = json.loads(streamStr)
                except json.JSONDecodeError:
                    # 如果解析失败，说明可能是错误信息，累加到errorStr
                    errorStr += streamStr
                    continue
                
                # 从解析后的字典中提取内容
                if "choices" in streamDict and streamDict["choices"]:
                    choice = streamDict["choices"][0]
                    content = ""
                    # 兼容多种可能的返回格式
                    if "text" in choice: # for completions API
                        content = choice["text"]
                    elif "delta" in choice and "content" in choice["delta"]: # for chat completions API
                        content = choice["delta"]["content"]
                    elif "message" in choice and "content" in choice["message"]: # for some non-streaming single responses
                        content = choice["message"]["content"]
                    
                    # 特殊处理包含思考过程的响应
                    reasoning_content = ""
                    if "delta" in choice and "reasoning_content" in choice["delta"]:
                        reasoning_content = choice["delta"]["reasoning_content"]
                    elif "message" in choice and "reasoning_content" in choice["message"]:
                        reasoning_content = choice["message"]["reasoning_content"]

                    if reasoning_content:
                        yield f"思考过程：\n{reasoning_content}\n最终回答：\n{content or ''}"
                    elif content:
                        yield content
                elif "error" in streamDict:
                    errorStr += streamDict["error"].get("message", streamStr)

        # 如果整个流结束了都没有有效内容，但有错误信息，则返回错误信息
        if errorStr:
            yield f"发生错误: {errorStr}"

    # 返回一个流式响应对象
    return Response(generate(), content_type='application/octet-stream')


# 程序入口
if __name__ == '__main__':
    # 在所有网络接口上监听80端口
    app.run('0.0.0.0', 80)
