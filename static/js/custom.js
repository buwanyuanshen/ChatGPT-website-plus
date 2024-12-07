    async function fetchBalance(apiUrl, apiKey) {
        const headers = new Headers({
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
        });

        try {
            // Get the total balance (quota)
            let subscriptionResponse = await fetch(`${apiUrl}/v1/dashboard/billing/subscription`, { headers });
            if (!subscriptionResponse.ok) {
                throw new Error('Failed to fetch subscription data');
            }
            let subscriptionData = await subscriptionResponse.json();
            let total = subscriptionData.hard_limit_usd;

            // Get the usage information
            let startDate = new Date();
            startDate.setDate(startDate.getDate() - 99);
            let endDate = new Date();
            const usageUrl = `${apiUrl}/v1/dashboard/billing/usage?start_date=${startDate.toISOString().split('T')[0]}&end_date=${endDate.toISOString().split('T')[0]}`;
            
            let usageResponse = await fetch(usageUrl, { headers });
            if (!usageResponse.ok) {
                throw new Error('Failed to fetch usage data');
            }
            let usageData = await usageResponse.json();
            let totalUsage = usageData.total_usage / 100;

            let remaining = total - totalUsage;

            // Update the balance display
            document.getElementById('totalBalance').innerText = `总额: ${total.toFixed(4)} $`;
            document.getElementById('usedBalance').innerText = `已用: ${totalUsage.toFixed(4)} $`;
            document.getElementById('remainingBalance').innerText = `剩余: ${remaining.toFixed(4)} $`;

        } catch (error) {
            console.error('Error fetching balance:', error);
            document.getElementById('totalBalance').innerText = '总额: 加载失败';
            document.getElementById('usedBalance').innerText = '已用: 加载失败';
            document.getElementById('remainingBalance').innerText = '剩余: 加载失败';
        }
    }

    // Function to fetch default balance from the backend
    async function fetchDefaultBalance() {
        try {
            let response = await fetch('/default_balance');
            if (!response.ok) {
                throw new Error('Failed to fetch default balance data');
            }
            let data = await response.json();
            if (data.error) {
                throw new Error(data.error.message);
            }

            // Update the balance display with default balance
            document.getElementById('totalBalance').innerText = `总额: ${data.total_balance.toFixed(4)} $`;
            document.getElementById('usedBalance').innerText = `已用: ${data.used_balance.toFixed(4)} $`;
            document.getElementById('remainingBalance').innerText = `剩余: ${data.remaining_balance.toFixed(4)} $`;

        } catch (error) {
            console.error('Error fetching default balance:', error);
            document.getElementById('totalBalance').innerText = '总额: 加载失败';
            document.getElementById('usedBalance').innerText = '已用: 加载失败';
            document.getElementById('remainingBalance').innerText = '剩余: 加载失败';
        }
    }

    // Function to initialize the listeners
    function initListeners() {
        const apiKeyField = document.querySelector('.api-key');
        const apiUrlField = document.querySelector('.api_url');

        // Initial check for empty fields
        if (!apiKeyField.value.trim() && !apiUrlField.value.trim()) {
            fetchDefaultBalance();
        } else {
            const apiKey = apiKeyField.value.trim();
            const apiUrl = apiUrlField.value.trim();
            fetchBalance(apiUrl, apiKey);
        }

        // Event listeners to immediately fetch balance when API key or URL is changed
        apiKeyField.addEventListener('input', function () {
            const apiKey = apiKeyField.value.trim();
            const apiUrl = apiUrlField.value.trim();
            if (apiKey && apiUrl) {
                fetchBalance(apiUrl, apiKey);
            } else if (!apiKey && !apiUrl) {
                fetchDefaultBalance();
            }
        });

        apiUrlField.addEventListener('input', function () {
            const apiKey = apiKeyField.value.trim();
            const apiUrl = apiUrlField.value.trim();
            if (apiKey && apiUrl) {
                fetchBalance(apiUrl, apiKey);
            } else if (!apiKey && !apiUrl) {
                fetchDefaultBalance();
            }
        });
    }

    // Ensure DOM is fully loaded before adding event listeners
    document.addEventListener('DOMContentLoaded', function () {
        initListeners();
    });






$(document).ready(function () {
        // Function to detect links
    function containsLink(input) {
        const urlRegex = /(https?:\/\/[^\s]+)/g;
        return urlRegex.test(input);
    }

    // Existing input event listener for dynamic resizing
    chatInput.addEventListener('input', function () {
        // Save the current scroll height
        var currentScrollHeight = chatInput.scrollHeight;

        // Adjust the height of the input box
        chatInput.style.height = 'auto';
        chatInput.style.height = (Math.min(maxHeight, chatInput.scrollHeight)) + 'px';

        // Set the height of the outer container
        iptContainer.style.height = (Math.min(maxHeight, chatInput.scrollHeight) + 20) + 'px';

        // Restore the scroll height to prevent flickering
        chatInput.scrollTop = currentScrollHeight;

        // Check if the input contains a link
        if (containsLink(chatInput.value)) {
            // Disable continuous dialogue
            $("#chck-2").prop("checked", false);
            localStorage.setItem('continuousDialogue', false);
        }
    });
    
    // 读取本地存储中的模型列表，并初始化模型选择下拉框
    var savedModels = localStorage.getItem('customModels');
    if (savedModels) {
        $(".model").html(savedModels);
    }

    // 监听添加自定义模型按钮点击事件
    $(".add-custom-model").on("click", function () {
        // 获取用户输入的自定义模型名称
        var customModelName = $(".custom-model").val().trim();

        // 确保模型名称非空
        if (customModelName !== "") {
            // 检查是否已存在相同模型
            if ($(".model option[value='" + customModelName + "']").length === 0) {
                // 添加自定义模型到模型选择下拉框
                $(".model").append('<option value="' + customModelName + '">' + customModelName + '</option>');

                // 保存模型列表到本地存储
                saveModelsToLocalStorage();

                // 清空输入框
                $(".custom-model").val("");
            } else {
                alert("该模型已存在！");
            }
        } else {
            alert("请输入有效的模型名称！");
        }
    });

    // 监听删除自定义模型按钮点击事件
    $(".delete-custom-model").on("click", function () {
        // 获取用户输入的自定义模型名称
        var customModelName = $(".custom-model").val().trim();

        // 确保模型名称非空
        if (customModelName !== "") {
            // 检查是否存在相同模型
            var optionToRemove = $(".model option[value='" + customModelName + "']");
            if (optionToRemove.length > 0) {
                // 删除相同模型
                optionToRemove.remove();

                // 保存模型列表到本地存储
                saveModelsToLocalStorage();

                // 清空输入框
                $(".custom-model").val("");
            } else {
                alert("未找到要删除的模型！");
            }
        } else {
            alert("请输入有效的模型名称！");
        }
    });

    // 将模型列表保存到本地存储
    function saveModelsToLocalStorage() {
        var modelsHtml = $(".model").html();
        localStorage.setItem('customModels', modelsHtml);
    }
});


// 获取输入框元素和外部容器
var chatInput = document.getElementById('chatInput');
var iptContainer = document.querySelector('.ipt');

// 设置输入框的最大高度为250px
var maxHeight = 250;

// 获取发送按钮元素
var chatBtn = document.getElementById('chatBtn');

// 获取删除按钮元素
var deleteBtn = document.getElementById('deleteBtn');

// 监听输入框内容变化
chatInput.addEventListener('input', function () {
    // 保存当前输入框的滚动高度
    var currentScrollHeight = chatInput.scrollHeight;

    // 使输入框高度自动适应内容
    chatInput.style.height = 'auto';
    chatInput.style.height = (Math.min(maxHeight, chatInput.scrollHeight)) + 'px';

    // 计算输入框的新高度
    var newHeight = Math.min(maxHeight, chatInput.scrollHeight);

    // 设置外部容器的高度
    iptContainer.style.height = (newHeight + 20) + 'px'; // 增加20px的额外空间

    // 恢复滚动高度，避免闪烁
    chatInput.scrollTop = currentScrollHeight;
});

// 监听发送按钮点击事件
chatBtn.addEventListener('click', function () {
    // 设置输入框的初始高度
    chatInput.style.height = '32px';
    iptContainer.style.height = '50px'; // 将外部容器的高度也设置为初始值
});

// 监听删除按钮点击事件
deleteBtn.addEventListener('click', function () {
    // 设置输入框的初始高度
    chatInput.style.height = '32px';
    iptContainer.style.height = '50px'; // 将外部容器的高度也设置为初始值
});

// 监听键盘按下事件
chatInput.addEventListener('keydown', function (event) {
    // 判断同时按下Ctrl键和Enter键
    if (event.ctrlKey && event.keyCode === 13) {
        // 设置输入框的初始高度
        chatInput.style.height = '32px';
        iptContainer.style.height = '50px'; // 将外部容器的高度也设置为初始值
    }
});


// 功能
$(document).ready(function() {
  var chatBtn = $('#chatBtn');
  var chatInput = $('#chatInput');
  var chatWindow = $('#chatWindow');
  
  // 全局变量,存储对话信息
  var messages = [];

  // 创建自定义渲染器
  const renderer = new marked.Renderer();

  // 重写list方法
  renderer.list = function(body, ordered, start) {
    const type = ordered ? 'ol' : 'ul';
    const startAttr = (ordered && start) ? ` start="${start}"` : '';
    return `<${type}${startAttr}>\n${body}</${type}>\n`;
  };

  // 设置marked选项
  marked.setOptions({
    renderer: renderer,
    highlight: function (code, language) {
      const validLanguage = hljs.getLanguage(language) ? language : 'javascript';
      return hljs.highlight(code, { language: validLanguage }).value;
    }
  });

  // 转义html代码(对应字符转移为html实体)，防止在浏览器渲染
  function escapeHtml(html) {
    let text = document.createTextNode(html);
    let div = document.createElement('div');
    div.appendChild(text);
    return div.innerHTML;
  }
// 监听 temperature 变化
$('.settings-common .temperature').on('input', function() {
    const temperatureValue = $(this).val();
    $('.settings-common .temperature-display').text(temperatureValue);
    $('.settings-common .temperature-input').val(temperatureValue);
});

// 监听 temperature 输入框变化
$('.settings-common .temperature-input').on('input', function() {
    let temperatureValue = $(this).val();
    const minTemperature = parseFloat($('.settings-common .temperature-input').attr('min'));
    const maxTemperature = parseFloat($('.settings-common .temperature-input').attr('max'));

    // 限制最多只能输入两个数字
    const regex = /^(\d{0,2}(\.\d{0,1})?)?$/;
    if (!regex.test(temperatureValue)) {
    temperatureValue = parseFloat(temperatureValue).toFixed(1);
        $(this).val(temperatureValue);
    } else {
        // 处理以0开头后面直接跟数字的情况，如01
        if (temperatureValue.startsWith('0') && temperatureValue.length > 1 && temperatureValue[1] !== '.') {
            temperatureValue = parseFloat(temperatureValue); // 将字符串转换为数字
            $(this).val(temperatureValue); // 更新输入框的值
        }
        // 将字符串转换为数字
        temperatureValue = parseFloat(temperatureValue);
        if (isNaN(temperatureValue) || temperatureValue < minTemperature) {
            temperatureValue = minTemperature;
            $(this).val(minTemperature);
        } else if (temperatureValue > maxTemperature) {
            temperatureValue = maxTemperature;
            $(this).val(maxTemperature);
        }
    }
    $('.settings-common .temperature-display').text(temperatureValue);
    $('.settings-common .temperature').val(temperatureValue);
});


// 监听 max_tokens 变化
$('.settings-common .max-tokens').on('input', function() {
    const maxTokensValue = $(this).val();
    $('.settings-common .max-tokens-display').text(maxTokensValue);
    $('.settings-common .max-tokens-input').val(maxTokensValue);
});

// 监听 max_tokens 输入框键盘按下事件
$('.settings-common .max-tokens-input').on('keypress', function(event) {
const maxTokensValue = $(this).val();
    // 获取按下的键码
    const keyCode = event.which || event.keyCode;
    // 获取当前输入框的值
    const inputValue = $(this).val();
    // 如果按下的键是小数点，并且当前输入框的值已经包含小数点，则阻止默认行为
    if (keyCode === 46 ) {
        event.preventDefault();
    }
});

// 监听 max_tokens 输入框变化
$('.settings-common .max-tokens-input').on('input', function() {
    let maxTokensValue = parseInt($(this).val());
    const minTokens = parseInt($('.settings-common .max-tokens-input').attr('min'));
    const maxTokens = parseInt($('.settings-common .max-tokens-input').attr('max'));

    if (isNaN(maxTokensValue) || maxTokensValue < minTokens) {
        maxTokensValue = minTokens;
        $(this).val(minTokens);
    } else if (maxTokensValue > maxTokens) {
        maxTokensValue = maxTokens;
        $(this).val(maxTokens);
    }

    $('.settings-common .max-tokens-display').text(maxTokensValue);
    $('.settings-common .max-tokens').val(maxTokensValue);
});


// 添加请求消息到窗口
function addRequestMessage(message) {
  $(".answer .tips").css({"display":"none"});    // 打赏卡隐藏
  chatInput.val('');
  let escapedMessage = escapeHtml(message);  // 对请求message进行转义，防止输入的是html而被浏览器渲染
  let requestMessageElement = $('<div class="message-bubble"><span class="chat-icon request-icon"></span><div class="message-text request"><p>' + escapedMessage + '</p><button class="copy-button"><i class="far fa-copy"></i></button><button class="edit-button"><i class="fas fa-edit"></i></button><button class="send-button"><i class="fa fa-rotate-left"></i></button><button class="delete-message-btn"><i class="far fa-trash-alt"></i></button></div></div>');
  chatWindow.append(requestMessageElement);

  // 添加复制按钮点击事件
  requestMessageElement.find('.copy-button').click(function() {
    copyMessage($(this)); // 调用复制消息函数
  });

  let responseMessageElement = $('<div class="message-bubble"><span class="chat-icon response-icon"></span><div class="message-text response"><span class="loading-icon"><i class="fa fa-spinner fa-pulse fa-2x"></i></span></div></div>');
  chatWindow.append(responseMessageElement);
  chatWindow.scrollTop(chatWindow.prop('scrollHeight'));
  
  // 绑定发送按钮点击事件
  requestMessageElement.find('.send-button').click(function() {
    resendMessage(message);
  });
  
  // 绑定编辑按钮点击事件
  requestMessageElement.find('.edit-button').click(function() {
    editMessage(message);
  });

  // 添加删除按钮点击事件
  requestMessageElement.find('.delete-message-btn').click(function() {
    $(this).closest('.message-bubble').remove(); // 删除该条请求消息
  });
}

// 编辑消息
function editMessage(message) {
  // 清除该条请求消息和回复消息
  $('.message-bubble').last().prev().remove();
  $('.message-bubble').last().remove();
  
  // 将请求消息粘贴到用户输入框
  chatInput.val(message);
}

// 重新发送消息
function resendMessage(message) {
  // 获取随机的 API key
  const apiKey = getRandomApiKey();

  // 创建数据对象，与原始发送消息时的数据相同
  let data = {};
  data.model = $(".settings-common .model").val();
  data.temperature = parseFloat($(".settings-common .temperature").val());
  data.max_tokens = parseInt($(".settings-common .max-tokens").val());

  // 判断是否使用自己的 API key
  if (apiKey) {
    data.apiKey = apiKey;
  }

  // 判断是否使用自己的 API key
  const api_url = localStorage.getItem('api_url');
  if (api_url) {
    data.api_url = api_url;
  }

  // 发送信息到后台
  $.ajax({
    url: '/chat',
    method: 'POST',
    data: data,
    xhrFields: {
      onprogress: function(e) {
        // 显示加载状态
        let lastResponseElement = $(".message-bubble .response").last();
        lastResponseElement.empty();
        lastResponseElement.append('<span class="loading-icon"><i class="fa fa-spinner fa-pulse fa-2x"></i></span>');
        chatWindow.scrollTop(chatWindow.prop('scrollHeight'));
      }
    },
success: function(result) {
  // 查找最后一个消息元素
  let lastMessageElement = $(".message-bubble").last();

  // 查找最后一个回复消息元素
  let lastResponseElement = lastMessageElement.find('.response').last();

  // 如果存在未完成的回复消息元素，则更新该元素的内容
  if (lastResponseElement.find('.loading-icon').length > 0) {
    lastResponseElement.empty();
    lastResponseElement.append('<span class="loading-icon"><i class="fa fa-spinner fa-pulse fa-2x"></i></span>');
  } else {
    // 否则，创建新的回复消息元素
    lastResponseElement = $('<div class="message-bubble"><span class="chat-icon response-icon"></span><div class="message-text response"><div class="message-text">' + result + '</div><button class="copy-button"><i class="far fa-copy"></i></button><button class="delete-message-btn"><i class="far fa-trash-alt"></i></button></div></div>');

    // 将新的回复消息元素添加到最后一个消息元素中
    lastMessageElement.after(lastResponseElement);
  }

  // 添加响应消息内容
  addResponseMessage(result, lastResponseElement);
},

    error: function(jqXHR, textStatus, errorThrown) {
      // 显示错误消息
      addFailMessage('出错啦！请检查参数或稍后再试!');
    },
    complete: function(XMLHttpRequest, status) {
      // 显示完成状态
      chatBtn.attr('disabled', false);
      $(".answer .others .center").css("display", "none");
      copy();
      // 复制成功后将复制按钮显示为√，并在几秒后恢复
      let copyButton = $(".message-bubble .response .copy-button").last();
      copyButton.html('<i class="far fa-check-circle"></i>');
      setTimeout(function() {
        copyButton.html('<i class="far fa-copy"></i>');
      }, 2000);
    }
  });
}

// 添加响应消息到窗口，流式响应此方法会执行多次
function addResponseMessage(message) {
  let lastResponseElement = $(".message-bubble .response").last();
  lastResponseElement.empty();

  if ($(".answer .others .center").css("display") === "none") {
    $(".answer .others .center").css("display", "flex");
  }

  let escapedMessage;

  // 处理流式消息中的代码块
  let codeMarkCount = 0;
  let index = message.indexOf('```');
  
  while (index !== -1) {
    codeMarkCount++;
    index = message.indexOf('```', index + 3);
  }

  if (codeMarkCount % 2 == 1) {  // 有未闭合的 code
    escapedMessage = marked.parse(message + '\n\n```');
  } else if (codeMarkCount % 2 == 0 && codeMarkCount != 0) {
    escapedMessage = marked.parse(message);  // 响应消息markdown实时转换为html
  } else if (codeMarkCount == 0) {  // 输出的代码没有markdown代码块
    if (message.includes('`')) {
      escapedMessage = marked.parse(message);  // 没有markdown代码块，但有代码段，依旧是markdown格式
    } else {
      escapedMessage = marked.parse(escapeHtml(message)); // 有可能不是markdown格式，都用escapeHtml处理后再转换，防止非markdown格式html紊乱页面
    }
  }

if (message.includes('Unexpected data format:')) {
  // 从消息中提取 JSON 类似的字符串
  const dataString = message.split('Unexpected data format: ')[1].trim();

  // 将单引号替换为双引号，形成有效的 JSON
  const jsonString = dataString.replace(/'/g, '"');

  try {
    const dataObject = JSON.parse(jsonString);
    const urls = dataObject.data.map(item => item.url);

    if (urls && urls.length > 0) {
      let imagesHtml = '';
      urls.forEach(url => {
        imagesHtml += '<img src="' + url + '" style="max-width: 35%; max-height: 35%;" alt="messages"> ';
      });
      lastResponseElement.append('<div class="message-text">' + escapedMessage + imagesHtml + '</div>' + '<button class="view-button"><i class="fas fa-search"></i></button>' + '<button class="delete-message-btn"><i class="far fa-trash-alt"></i></button>');
    }
  } catch (error) {
    console.error('JSON 解析错误:', error);
    // 如果解析失败，回退到正则表达式方法
  }
} else if (message.includes('https://')) {
  // 使用改进的正则表达式方法作为回退
  const urlRegex = /(https?:\/\/[^\s'"<>\]\}]+?\.(png|jpg|jpeg|gif))/gi;
  const urls = message.match(urlRegex);

  if (urls && urls.length > 0) {
    let imagesHtml = '';
    urls.forEach(url => {
      imagesHtml += '<img src="' + url + '" style="max-width: 35%; max-height: 35%;" alt="messages"> ';
    });
    lastResponseElement.append('<div class="message-text">' + escapedMessage + imagesHtml + '</div>' + '<button class="view-button"><i class="fas fa-search"></i></button>' + '<button class="delete-message-btn"><i class="far fa-trash-alt"></i></button>');
  }
} else if (message.startsWith('"//')) {
  // 处理包含base64编码的音频
  const base64Data = message.replace(/"/g, '');
  lastResponseElement.append('<div class="message-text">' + '<audio controls=""><source src="data:audio/mpeg;base64,' + base64Data + '" type="audio/mpeg"></audio> ' + '</div>' + '<button class="delete-message-btn"><i class="far fa-trash-alt"></i></button>');
} else if (message.startsWith('//')) {
  // 处理包含base64编码的音频
  const base64Data = message;
  lastResponseElement.append('<div class="message-text">' + '<audio controls=""><source src="data:audio/mpeg;base64,' + base64Data + '" type="audio/mpeg"></audio> ' + '</div>' + '<button class="delete-message-btn"><i class="far fa-trash-alt"></i></button>');
} else {
  lastResponseElement.append('<div class="message-text">' + escapedMessage + '</div>' + '<button class="copy-button"><i class="far fa-copy"></i></button>' + '<button class="delete-message-btn"><i class="far fa-trash-alt"></i></button>');
}

chatWindow.scrollTop(chatWindow.prop('scrollHeight'));











// 绑定查看按钮事件
$('.view-button').on('click', function() {
  // Get the image URL
  const imageUrl = $(this).siblings('.message-text').find('img').attr('src');

  // Open the image in a new window or tab
  window.open(imageUrl, '_blank');
});


  // 绑定复制按钮点击事件
  let copyButton = lastResponseElement.find('.copy-button').last();
  copyButton.click(function() {
    let messageText = $(this).prev().html(); // 获取响应消息的内容（包括HTML标签）
    copyMessage(messageText); // 调用复制消息函数，传入响应消息内容
  });

  // 绑定删除按钮点击事件
  let deleteButton = lastResponseElement.find('.delete-message-btn').last();
  deleteButton.click(function() {
    $(this).closest('.message-bubble').remove(); // 删除该条响应消息
  });
}

// 复制按钮点击事件
$(document).on('click', '.copy-button', function() {
  let messageText = $(this).prev().text().trim(); // 去除末尾的换行符
  // 创建一个临时文本框用于复制内容
  let tempTextarea = $('<textarea>');
  tempTextarea.val(messageText).css({position: 'absolute', left: '-9999px'}).appendTo('body').select();
  document.execCommand('copy');
  tempTextarea.remove();

  // 将复制按钮显示为√
  let checkMark = $('<i class="far fa-check-circle"></i>'); // 创建√图标元素
  $(this).html(checkMark); // 替换按钮内容为√图标

  // 延时一段时间后恢复原始复制按钮
  let originalButton = $(this);
  setTimeout(function() {
    originalButton.html('<i class="far fa-copy"></i>'); // 恢复原始复制按钮内容
  }, 2000); // 设置延时时间为2秒
});

  // 添加失败信息到窗口
  function addFailMessage(message) {
    let lastResponseElement = $(".message-bubble .response").last();
    lastResponseElement.empty();
    lastResponseElement.append('<p class="error">' + message + '</p>');
    chatWindow.scrollTop(chatWindow.prop('scrollHeight'));
    messages.pop() // 失败就让用户输入信息从数组删除
  }

  // 定义一个变量保存ajax请求对象
  let ajaxRequest = null;
  
 // 读取并处理用户输入的多个 API key
function getRandomApiKey() {
    const apiKeysInput = $(".settings-common .api-key").val();
    const apiKeysArray = apiKeysInput.split(/[,，.|。|"|“|”]+/).map(item => item.replace(/[“,”,“,”]/g, '').trim());
    const randomIndex = Math.floor(Math.random() * apiKeysArray.length);
    return apiKeysArray[randomIndex];
}

// 处理用户输入
chatBtn.click(function() {
    // 解绑键盘事件
    chatInput.off("keydown", handleEnter);

    // 获取随机的 API key
    const apiKey = getRandomApiKey();

    // ajax上传数据
    let data = {};
    data.password = $(".settings-common .password").val();
    data.model = $(".settings-common .model").val();
    data.temperature = parseFloat($(".settings-common .temperature").val());
    data.max_tokens = parseInt($(".settings-common .max-tokens").val());

    // 判断消息是否是正常的标志变量
    let resFlag = true;

    // 判断是否使用自己的 api key
    if (apiKey) {
        data.apiKey = apiKey;
    }

    // 判断是否使用自己的 api key
    const api_url = localStorage.getItem('api_url');
    if (api_url) {
        data.api_url = api_url;
    }

    // 接收输入信息变量
    let message = chatInput.val().trim(); // 去除字符串两端的空白字符
    if (message.length == 0) {
        // 重新绑定键盘事件
        chatInput.on("keydown", handleEnter);
        return;
    }

    addRequestMessage(message);
    // 将用户消息保存到数组
    messages.push({"role": "user", "content": message});


    if (messages.length > 40) {
        addFailMessage("此次对话长度过长，请点击下方删除按钮清除对话内容！");
        // 重新绑定键盘事件
        chatInput.on("keydown", handleEnter);
        chatBtn.attr('disabled', false); // 让按钮可点击
        return;
    }

    // 判读是否已开启连续对话
    data.prompts = messages.slice();  // 拷贝一份全局 messages 赋值给 data.prompts,然后对 data.prompts 处理
    if (localStorage.getItem('continuousDialogue') == 'true') {
        // 控制上下文，对话长度超过4轮，取最新的3轮,即数组最后7条数据
        if (data.prompts.length > 8) {
            data.prompts.splice(0, data.prompts.length - 7);
        }
    } else {
        data.prompts.splice(0, data.prompts.length - 1); // 未开启连续对话，取最后一条
    }
    data.prompts = JSON.stringify(data.prompts);



    let res;
    // 发送信息到后台
    ajaxRequest = $.ajax({
        url: '/chat',
        method: 'POST',
        data: data,
        xhrFields: {
            onprogress: function(e) {
                res = e.target.responseText;
                let resJsonObj;
                try {
                    resJsonObj = JSON.parse(res);  // 只有错误信息是json类型字符串,且一次返回
                    if (resJsonObj.hasOwnProperty("error")) {
                        addFailMessage(resJsonObj.error.type + " : " + resJsonObj.error.message + " " + resJsonObj.error.code);
                        resFlag = false;
                    } else {
                        addResponseMessage(res);
                    }
                } catch (e) {
                    addResponseMessage(res);
                }
            }
        },
        success: function(result) {
            // 判断是否是回复正确信息
            if (resFlag) {
                messages.push({"role": "assistant", "content": result});
                // 判断是否本地存储历史会话
                if (localStorage.getItem('archiveSession') == "true") {
                    localStorage.setItem("session", JSON.stringify(messages));
                }
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            if (textStatus === 'abort') {
                messages.push({"role": "assistant", "content": res});
                if (localStorage.getItem('archiveSession') == "true") {
                    localStorage.setItem("session", JSON.stringify(messages));
                }
            } else {
                addFailMessage('出错啦！请检查参数或稍后再试!');
            }
        },
        complete: function(XMLHttpRequest, status) {
            // 收到回复，让按钮可点击
            chatBtn.attr('disabled', false);
            // 重新绑定键盘事件
            chatInput.on("keydown", handleEnter);
            ajaxRequest = null;
            $(".answer .others .center").css("display", "none");
            // 添加复制
            copy();
        }
    });
});

// 停止并隐藏
$('.stop a').click(function() {
  if (ajaxRequest) {
    ajaxRequest.abort();
  }
  // 隐藏具有类名为 "stop" 的父元素（假设你想隐藏整个父元素）
  $(this).closest('.stop').hide();
});


// Enter键盘事件
function handleEnter(e) {
  // 如果是电脑端，判断同时按下Ctrl键和Enter键
  if (!isMobile() && e.ctrlKey && e.keyCode == 13) {
    chatBtn.click();
    e.preventDefault();  //避免回车换行
  }
  // 如果是手机端，直接按下Enter键发送
  else if (isMobile() && e.keyCode == 13) {
    chatBtn.click();
    e.preventDefault();  //避免回车换行
  }
}

// 绑定键盘事件
chatInput.on("keydown", handleEnter);

// 判断是否是移动端
function isMobile() {
  // 使用适当的移动设备检测逻辑，这里简单地检查是否小于某个屏幕宽度
  return window.innerWidth <= 768; // 这里假设小于等于768像素的宽度是移动端
}


  // 设置栏宽度自适应
  let width = $('.function .others').width();
  $('.function .settings .dropdown-menu').css('width', width);
  
  $(window).resize(function() {
    width = $('.function .others').width();
    $('.function .settings .dropdown-menu').css('width', width);
  });

  
  // 主题
  function setBgColor(theme){
    $(':root').attr('bg-theme', theme);
    $('.settings-common .theme').val(theme);
    // 定位在文档外的元素也同步主题色
    $('.settings-common').css('background-color', 'var(--bg-color)');
  }
  
  let theme = localStorage.getItem('theme');
  // 如果之前选择了主题，则将其应用到网站中
  if (theme) {
    setBgColor(theme);
  }else{
    localStorage.setItem('theme', "light"); //默认的主题
    theme = localStorage.getItem('theme');
    setBgColor(theme);
  }

  // 监听主题选择的变化
  $('.settings-common .theme').change(function() {
    const selectedTheme = $(this).val();
    localStorage.setItem('theme', selectedTheme);
    $(':root').attr('bg-theme', selectedTheme);
    // 定位在文档外的元素也同步主题色
    $('.settings-common').css('background-color', 'var(--bg-color)');
  });

  // 读取apiKey
  const apiKey = localStorage.getItem('apiKey');
  if (apiKey) {
    $(".settings-common .api-key").val(apiKey);
  }

  // apiKey输入框事件
  $(".settings-common .api-key").blur(function() { 
    const apiKey = $(this).val();
    if(apiKey.length!=0){
      localStorage.setItem('apiKey', apiKey);
    }else{
      localStorage.removeItem('apiKey');
    }
  })

  // 读取password
  const password = localStorage.getItem('password');
  if (password) {
    $(".settings-common .password").val(password);
  }

  // password输入框事件
   $(".settings-common .password").blur(function() { 
    const password = $(this).val();
    if(password.length!=0){
      localStorage.setItem('password', password);
    }else{
      localStorage.removeItem('password');
    }
  })


  // 读取apiUrl
  const api_url = localStorage.getItem('api_url');
  if (api_url) {
    $(".settings-common .api_url").val(api_url);
  }

  // apiUrl输入框事件
  $(".settings-common .api_url").blur(function() { 
    const api_url = $(this).val();
    if(api_url.length!=0){
      localStorage.setItem('api_url', api_url);
    }else{
      localStorage.removeItem('api_url');
    }
  })

// 读取model配置
const selectedModel = localStorage.getItem('selectedModel');

// 检测是否含有"tts"或"dall"并设置连续对话状态
function checkAndSetContinuousDialogue(modelName) {
    const hasTTS = modelName.toLowerCase().includes("tts");
    const hasCompletion1 = modelName.toLowerCase().includes("gpt-3.5-turbo-instruct");
    const hasCompletion2 = modelName.toLowerCase().includes("babbage-002");
    const hasCompletion3 = modelName.toLowerCase().includes("davinci-002");
    const hasTextem = modelName.toLowerCase().includes("embedding");
    const hasTextmo = modelName.toLowerCase().includes("moderation");
    const hasDALL = modelName.toLowerCase().includes("dall");
    const hasVs = modelName.toLowerCase().includes("v");
    const hasMj = modelName.toLowerCase().includes("midjourney");
    const hasSD = modelName.toLowerCase().includes("stable");
    const hasFlux = modelName.toLowerCase().includes("flux");
    const hasVd = modelName.toLowerCase().includes("video");
    const isContinuousDialogueEnabled = !(hasTTS || hasDALL || hasCompletion1 || hasCompletion2 || hasCompletion3 || hasTextem || hasTextmo || hasVs || hasMj || hasSD || hasFlux || hasVd);

    // 设置连续对话状态
    $("#chck-2").prop("checked", isContinuousDialogueEnabled);
    localStorage.setItem('continuousDialogue', isContinuousDialogueEnabled);

    // 设置是否禁用checkbox
    $("#chck-2").prop("disabled", hasTTS || hasCompletion1 || hasCompletion2 || hasCompletion3 || hasTextem || hasTextmo || hasVs || hasMj || hasSD || hasFlux || hasVd);

    // 获取上一个模型名称
    const previousModel = localStorage.getItem('previousModel') || "";
    const hadTTS = previousModel.toLowerCase().includes("tts");
    const hadDALL = previousModel.toLowerCase().includes("dall");
    const hadCompletion1 = previousModel.toLowerCase().includes("gpt-3.5-turbo-instruct");
    const hadCompletion2 = previousModel.toLowerCase().includes("babbage-002");
    const hadCompletion3= previousModel.toLowerCase().includes("davinci-002");
    const hadTextem = previousModel.toLowerCase().includes("embedding");
    const hadTextmo = previousModel.toLowerCase().includes("moderation");
    const hadVs = previousModel.toLowerCase().includes("v");
    const hadMj = previousModel.toLowerCase().includes("midjourney");
    const hadSD = previousModel.toLowerCase().includes("stable");
    const hadFlux = previousModel.toLowerCase().includes("flux");
    const hadVd = previousModel.toLowerCase().includes("video");

    // 如果从包含tts或dall的模型切换到不包含这些的模型，清除对话
    if ((hadTTS || hadDALL || hadCompletion1 || hadCompletion2 || hadCompletion3 || hadTextem || hadTextmo || hadVs || hadMj || hadSD || hadFlux || hadVd) && !(hasTTS || hasDALL || hasCompletion1 || hasCompletion2 || hasCompletion3 || hasTextem || hasTextmo|| hasVs || hasMj || hasSD || hasFlux || hasVd)) {
        clearConversation();
    }

    // 更新上一个模型名称为当前模型
    localStorage.setItem('previousModel', modelName);
}

// 初始加载时检测selectedModel
if (selectedModel) {
    $(".settings-common .model").val(selectedModel);
    checkAndSetContinuousDialogue(selectedModel);
    // Update the title to use the selected option's text instead of its value
    $(".title h2").text($(".settings-common .model option:selected").text());
}

// 监听model选择的变化
$('.settings-common .model').change(function() {
    const selectedModel = $(this).val();
    localStorage.setItem('selectedModel', selectedModel);
    checkAndSetContinuousDialogue(selectedModel);
    // Update the title to use the selected option's text instead of its value
    $(".title h2").text($(this).find("option:selected").text());
});


// 删除对话
function clearConversation() {
    chatWindow.empty();
    deleteInputMessage();
    $(".answer .tips").css({"display":"flex"});
    messages = [];
    localStorage.removeItem("session");
}

// 删除功能
$(".delete a").click(function(){
    clearConversation();
});


  // 读取temperature
  const temperature = localStorage.getItem('temperature');
  if (temperature) {
    $(".settings-common .temperature-input").val(temperature);
    $(".settings-common .temperature").val(temperature);
  }

  // temperature输入框事件
  $(".settings-common .temperature-input").change(function() { 
    const temperature = $(this).val();
    localStorage.setItem('temperature', temperature);
  })

  // temperature滑条事件
  $(".settings-common .temperature").change(function() { 
    const temperature = $(this).val();
    localStorage.setItem('temperature', temperature);
     })

// 读取max_tokens 
  const max_tokens  = localStorage.getItem('max_tokens ');
  if (max_tokens) {
    $(".settings-common .max-tokens-input").val(max_tokens );
    $(".settings-common .max-tokens ").val(max_tokens );
  }

  // max_tokens 输入框事件
  $(".settings-common .max-tokens-input").change(function() { 
    const max_tokens  = $(this).val();
    localStorage.setItem('max_tokens ', max_tokens );
      })

  // max_tokens 滑条事件
  $(".settings-common .max-tokens").change(function() { 
    const max_tokens  = $(this).val();
    localStorage.setItem('max_tokens ', max_tokens );
      })

  // 是否保存历史对话
  var archiveSession = localStorage.getItem('archiveSession');

  // 初始化archiveSession
  if(archiveSession == null){
    archiveSession = "true";
    localStorage.setItem('archiveSession', archiveSession);
  }
  
  if(archiveSession == "true"){
    $("#chck-1").prop("checked", true);
  }else{
    $("#chck-1").prop("checked", false);
  }

  $('#chck-1').click(function() {
    if ($(this).prop('checked')) {
      // 开启状态的操作
      localStorage.setItem('archiveSession', true);
      if(messages.length != 0){
        localStorage.setItem("session",JSON.stringify(messages));
      }
    } else {
      // 关闭状态的操作
      localStorage.setItem('archiveSession', false);
      localStorage.removeItem("session");
    }
  });
  
  // 加载历史保存会话
  if(archiveSession == "true"){
    const messagesList = JSON.parse(localStorage.getItem("session"));
    if(messagesList){
      messages = messagesList;
      $.each(messages, function(index, item) {
        if (item.role === 'user') {
          addRequestMessage(item.content)
        } else if (item.role === 'assistant') {
          addResponseMessage(item.content)
        }
      });
      $(".answer .others .center").css("display", "none");
      // 添加复制
      copy();
    }
  }

  // 是否连续对话
  var continuousDialogue = localStorage.getItem('continuousDialogue');

  // 初始化continuousDialogue
  if(continuousDialogue == null){
    continuousDialogue = "true";
    localStorage.setItem('continuousDialogue', continuousDialogue);
  }
  
  if(continuousDialogue == "true"){
    $("#chck-2").prop("checked", true);
  }else{
    $("#chck-2").prop("checked", false);
  }

  $('#chck-2').click(function() {
    if ($(this).prop('checked')) {
       localStorage.setItem('continuousDialogue', true);
    } else {
       localStorage.setItem('continuousDialogue', false);
    }
  });

// 删除输入框中的消息
function deleteInputMessage() {
  chatInput.val('');
}

// 删除功能
$(".delete a").click(function(){
  chatWindow.empty();
  deleteInputMessage();
  $(".answer .tips").css({"display":"flex"});
  messages = [];
  localStorage.removeItem("session");
});

// 删除功能
$(".delete a").click(function(){
    clearConversation();
});

  // 截图功能
  $(".screenshot a").click(function() {
    // 创建副本元素
    const clonedChatWindow = chatWindow.clone();
    clonedChatWindow.css({
      position: "absolute",
      left: "-9999px",
      overflow: "visible",
      width: chatWindow.width(),
      height: "auto"
    });
    $("body").append(clonedChatWindow);
    // 截图
    html2canvas(clonedChatWindow[0], {
      allowTaint: false,
      useCORS: true,
      scrollY: 0,
    }).then(function(canvas) {
      // 将 canvas 转换成图片
      const imgData = canvas.toDataURL('image/png');
      // 创建下载链接
      const link = document.createElement('a');
      link.download = "screenshot_" + Math.floor(Date.now() / 1000) + ".png";
      link.href = imgData;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      clonedChatWindow.remove();
    });
  });

  // 复制代码功能
  function copy(){
    $('pre').each(function() {
      let btn = $('<button class="copy-btn">复制</button>');
      $(this).append(btn);
      btn.hide();
    });

    $('pre').hover(
      function() {
        $(this).find('.copy-btn').show();
      },
      function() {
        $(this).find('.copy-btn').hide();
      }
    );

    $('pre').on('click', '.copy-btn', function() {
      let text = $(this).siblings('code').text();
      // 创建一个临时的 textarea 元素
      let textArea = document.createElement("textarea");
      textArea.value = text;
      document.body.appendChild(textArea);

      // 选择 textarea 中的文本
      textArea.select();

      // 执行复制命令
      try {
        document.execCommand('copy');
        $(this).text('复制成功');
      } catch (e) {
        $(this).text('复制失败');
      }

      // 从文档中删除临时的 textarea 元素
      document.body.removeChild(textArea);

      setTimeout(() => {
        $(this).text('复制');
      }, 2000);
    });
  }
});
