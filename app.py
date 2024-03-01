# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, render_template, Response
import requests
import json
import os
import random

app = Flask(__name__)

# 从配置文件中settings加载配置
app.config.from_pyfile('settings.py')

@app.route("/", methods=["GET"])
def index():
	return render_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat():
	messages = request.form.get("prompts", None)
	apiKey = request.form.get("apiKey", None)
	model = request.form.get("model", "gpt-3.5-turbo-0125")
	temperature = request.form.get("temperature", 0.5)
	max_tokens = request.form.get("max_tokens", 4000)
	password = request.form.get("password", None)
	# 获取用户输入的API URL
	api_url = request.form.get("api_url", None)

	# 如果用户没有输入API URL，则使用配置文件中的默认值
	if api_url is None:
		api_url = app.config.get("API_URL", None)
        
	# 设置gpt4授权码
	if password !="666666":
		if "gpt-4" in model:
			if apiKey is None:
				return jsonify({"error": {"message": "请联系群主获取授权码或者输入自己的apikey！", "type": "invalid_request_error", "code": ""}})

	if apiKey is None:
		if "gpt-4" in model:
			api_keys = app.config.get("API_KEYS1", [])
			apiKey = os.environ.get('OPENAI_API_KEY', random.choice(api_keys))
			api_url = app.config.get("API_URL1", None)
		else:
			api_keys = app.config.get("API_KEYS", [])
			apiKey = os.environ.get('OPENAI_API_KEY', random.choice(api_keys))

	headers = {
		"Content-Type": "application/json",
		"Authorization": f"Bearer {apiKey}",
	}

	# json串转对象
	prompts = json.loads(messages)

	data = {
		"messages": prompts,
		"model": model,
		"max_tokens": int(max_tokens),
		"temperature": float(temperature),
		"top_p": 1,
		"n": 1,
		"stream": True,
	}

	try:
		resp = requests.post(
			url=api_url + "/v1/chat/completions",
			headers=headers,
			json=data,
			stream=True,
			timeout=(60, 60)  # 连接超时时间为60秒，读取超时时间为60秒
		)
	except requests.exceptions.Timeout:
		return jsonify({"error": {"message": "请求超时，请稍后再试！", "type": "timeout_error", "code": ""}})
	except Exception as e:
		return jsonify({"error": {"message": str(e), "type": "unexpected_error", "code": ""}})

	# 迭代器实现流式响应
	def generate():
		errorStr = ""
		for chunk in resp.iter_lines():
			if chunk:
				streamStr = chunk.decode("utf-8").replace("data: ", "")
				try:
					streamDict = json.loads(streamStr)
				except:
					errorStr += streamStr.strip()
					continue

				# 检查 streamDict 是否包含 "choices" 键
				if "choices" in streamDict:
					delData = streamDict["choices"][0]
					if delData["finish_reason"] is not None:
						break
					else:
						if "content" in delData["delta"]:
							respStr = delData["delta"]["content"]
							yield respStr
				else:
					# 处理没有 "choices" 键的情况
					errorStr += f"Unexpected data format: {streamDict}"

		# 如果出现错误，此时错误信息迭代器已处理完，app_context已经出栈，要返回错误信息，需要将app_context手动入栈
		if errorStr != "":
			with app.app_context():
				yield errorStr

	return Response(generate(), content_type='application/octet-stream')

if __name__ == '__main__':
	app.run('0.0.0.0', 80)
