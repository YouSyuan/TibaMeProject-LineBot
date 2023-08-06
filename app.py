## ============================================
## -------                              -------
##        Line Bot 個人專題 - 角色辨識系統
##                   GCP 版本
## -------                              -------
## ============================================

import sys, os, requests, json
import numpy as np
from tensorflow import keras
# import tensorflow
from PIL import Image, ImageOps
# 引用 Web Server 套件
from flask import Flask, request, abort
# 引用 LineBot 相關套件
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models.template import *
from linebot.models.events import (
    FollowEvent, UnfollowEvent,
    MessageEvent, PostbackEvent,
    TextMessage, ImageMessage, VideoMessage, AudioMessage
    )
from linebot.models import(
    ImageSendMessage, TextSendMessage, 
    TemplateSendMessage, 
    PostbackTemplateAction,

    RichMenu,
    
    QuickReply, QuickReplyButton, 
    MessageAction, CameraAction, CameraRollAction, PostbackAction,
)

# 外部連結自動生成套件
# from pyngrok import ngrok

# 引入我的類別
from message_data import *
from QR_data import QRB

# gcp 套件
# logging 日誌
# https://googleapis.dev/python/logging/latest/stdlib-usage.html
import logging
import google.cloud.logging
from google.cloud.logging.handlers import CloudLoggingHandler
# cloud strage 值區
from google.cloud import storage
# firestore 資料庫
from google.cloud import firestore

# 圖片下載、上傳用
import urllib.request


## ==========================
##     建立日誌
## ==========================
# 啟用 log 客戶端
log_client = google.cloud.logging.Client()

# 建立 Line Event Log
# 記錄 line event
# CloudLoggingHandler 物件：處理事件的日誌紀錄
log = "cxcxc_bot_event"
bot_event_handler = CloudLoggingHandler(log_client, name=log)
# 日誌處理器：取得日誌紀錄對象
bot_event_logger = logging.getLogger(log)
# 處理日誌紀錄器的級別 ( INFO )
bot_event_logger.setLevel(logging.INFO)
bot_event_logger.addHandler(bot_event_handler)


## ==========================
##     主架構
## ==========================

# 設定 Server 啟用細節
app = Flask(__name__)

# 生成 line_bot_api, handler 實體物件
line_bot_api=LineBotApi(channel_access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
handler=WebhookHandler(channel_secret=os.environ["LINE_CHANNEL_SECRET"])

# 啟動server對外接口，使Line能丟消息進來
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    # Line 加密簽章
    signature = request.headers['X-Line-Signature']

    # get request body as text
    # 用戶傳來的內容
    body = request.get_data(as_text=True)
    # 將請求的主體資料記錄到日誌中
    bot_event_logger.info(body)

    # handle webhook body
    # 把消息交給 handler 做驗證
    # 會看是什麼樣的 Event，做不同的處理
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


## ==========================
##      關注
## ==========================
# 告知 handler，如果收到 FollowEvent，就執行下面的方法處理
@handler.add(FollowEvent)
def handle_follow(event):
    # 取得個資
    user_profile = line_bot_api.get_profile(event.source.user_id)

    # 從 line 取回照片，並放置在本地端
    user_pic_name = user_profile.user_id + ".jpg"
    urllib.request.urlretrieve(user_profile.picture_url, user_pic_name)

    # 設定儲存內容 Cloud Storage
    # 建立客戶端
    storage_client = storage.Client()
    # 桶子名稱
    bucket_name = os.environ['USER_INFO_GS_BUCKET_NAME']
    # 依照用戶 id 來命名大頭照名稱.png
    destination_blob_name = f"{user_profile.user_id}/user_pic.png"
    source_user_pic_name = user_pic_name
    # 進行上傳
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_user_pic_name)

    # 設定用戶資料 (json 檔)
    # 基本資料-字典
    user_dict = {
        "user_id"        : user_profile.user_id,
        "pricture_id"    : f"https://storage.googleapis.com/{bucket_name}/destination_blob_name",
        "disply_name"    : user_profile.display_name,
        "status_message" : user_profile.status_message,
    }
    # 加入 firestore
    # 建立客戶端
    db = firestore.Client()
    # 插入 line_user 表格 (主鍵為 user_id)
    doc_ref = db.collection("line-user").document(user_dict.get("user_id"))
    # 插入整筆資料
    doc_ref.set(user_dict)

    # 回覆內容   
    text_message_array = TextSendMessage(MyTextMessage.follow_text)
    image_message_array = ImageSendMessage(    
        original_content_url="https://i.imgur.com/NxbSs4L.jpg",
        preview_image_url="https://i.imgur.com/NxbSs4L.jpg"
    )
    line_bot_api.reply_message(event.reply_token, [image_message_array,text_message_array])

    # 創造圖文選單，綁定圖文選單
    # menu_pic_url = "https://i.imgur.com/T8mEFXt.jpg"    
    # menu_pic_url = Image.open("menu1.jpg")
    menu_pic_url = open("menu1.jpg", "rb")
    lineRichMenuId = MenuRawData.line_menu(line_bot_api)

    setImageResponse = line_bot_api.set_rich_menu_image(lineRichMenuId, "image/jpeg", menu_pic_url)

    line_bot_api.link_rich_menu_to_user(event.source.user_id, lineRichMenuId)
 


## ==========================
##      事件處理素材
## ==========================

say_hollo = MyTextMessage.say_hollo
button_template_message = TemplateSendMessage(
    alt_text = "Buttons template",
    template = ButtonsTemplate(
        thumbnail_image_url = "https://i.imgur.com/5yM71SX.jpg",
        title = "更多幫助",
        text = "請點擊下方按鈕",
        actions = [
            PostbackTemplateAction(label = "聯絡客服", text = "聯絡客服", data = "data1"),
            PostbackTemplateAction(label = "意見提供",text = "意見提供",data = "data2"),
            PostbackTemplateAction(label = "BUG 回報",text = "BUG 回報",data = "data3")
        ]
    )
)

# 設定字典，依照字典回應消息
message_dict = {
    "@more" : button_template_message,
}


## ==========================
##      辨識模組
## ==========================
class_dict = {}
with open("converted_savedmodel/labels.txt", "r", encoding="utf-8") as f:
    for line in f:
        (key, val) = line.split()
        class_dict[int(key)] = val

# Disable scientific notation for clarity 禁止科學計數法的使用
np.set_printoptions(suppress=True)

# 載入模組
# model = tensorflow.keras.models.load_model('converted_savedmodel/model.savedmodel')
model = keras.models.load_model('converted_savedmodel/model.savedmodel')

## ==========================
##      回傳消息執行程序
## ==========================
# 用戶發出文字消息時，按條件內容，回傳文字消息
@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    # 回應相對訊息
    if event.message.text in message_dict:
        line_bot_api.reply_message(event.reply_token, message_dict.get(event.message.text))
    elif event.message.text in say_hollo:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(event.message.text))
    elif event.message.text.find("@") == 0 and event.message.text != "@more":
        line_bot_api.reply_message(event.reply_token, TextSendMessage("感謝您寶貴的建議，我們將會參考您的意見，繼續優化與改進我們的服務。"))
    elif event.message.text.find("$") == 0:
        line_bot_api.reply_message(event.reply_token, TextSendMessage("感謝您找到系統的問題，我們已經將此問題回報給相關單位，以改善系統的問題。"))
    elif event.message.text.find("!") == 0:
        line_bot_api.reply_message(event.reply_token, TextSendMessage("辨識模組建構中，敬請期待！\nComing Soon..."))
    # 範本訊息
    elif event.message.text.find("@") != -1:
        line_bot_api.reply_message(event.reply_token, message_dict.get(event.message.text))


## ==========================
##      PostBack 處理
## ==========================
# 用戶點擊 button 後，觸發 postback event，對其回傳相對應處理
@handler.add(PostbackEvent)
def handle_post_message(event):
    if event.postback.data.find("data1") == 0:
        line_bot_api.reply_message(
            event.reply_token,
            TextMessage(text="請稍等，我們將以最快的速度與您聯絡。\n可以撥打客服專線：0987-654-321")
        )
    elif event.postback.data.find("data2") == 0:
        line_bot_api.reply_message(
            event.reply_token,
            TextMessage(text="請在開頭加上「@」再輸入您的建議。\n感謝您！")
        )
    elif event.postback.data.find("data3") == 0:
        line_bot_api.reply_message(
            event.reply_token,
            TextMessage(text="請在開頭加上「$」再輸入您的遇到的 BUG。\n感謝您！")
        )
    elif event.postback.data.find("@") != -1:
        line_bot_api.reply_message(
            event.reply_token,
            message_dict.get(event.message.text)
        )
    elif event.postback.data.find("!") == 0:
        pbd = event.postback.data
        if pbd in {"!pb", "!pb1", "!pb2", "!pb3", "!pb4"}:
            line_bot_api.reply_message(event.reply_token, QRB.qrb(event))        
        else:
            line_bot_api.reply_message(event.reply_token, QRB.qrb(event))
    elif event.postback.data == "指令":
        line_bot_api.reply_message(event.reply_token, TextMessage(text=MyTextMessage.postback_data.get(event.postback.data)))
    elif event.postback.data == "前往商店":
        line_bot_api.reply_message(event.reply_token, TextMessage(text=MyTextMessage.postback_data.get(event.postback.data)))
    elif event.postback.data == "最新消息":
        line_bot_api.reply_message(event.reply_token, TextMessage(text=MyTextMessage.postback_data.get(event.postback.data)))


## ==========================
##     圖片處理  解析圖片
## ==========================
@handler.add(MessageEvent, ImageMessage)
def handle_image_message(event):

    
    # 將圖片上傳到 cloud storage
    # 取出照片
    message_content = line_bot_api.get_message_content(event.message.id)
    file_name = event.message.id + ".png"
    with open(file_name, 'wb') as fd:
        for chunk in message_content.iter_content():
            fd.write(chunk)


    # 上傳至 cloud storage
    storage_client = storage.Client()
    bucket_name = os.environ['USER_INFO_GS_BUCKET_NAME']
    destination_blob_name = f'{event.source.user_id}/image/{event.message.id}.png'
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(file_name)

    
    ## 圖片辨識：
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)

    # Replace this with the path to your image 將其替換為圖像的路徑
    image = Image.open(file_name)

    # resize the image to a 224x224 with the same strategy as in TM2:
    # resizing the image to be at least 224x224 and then cropping from the center
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.LANCZOS)

    #turn the image into a numpy array 把圖像變成一個 numpy 數組
    image_array = np.asarray(image)

    # display the resized image
    # image.show()

    # Normalize the image 圖像標準化
    normalized_image_array = (image_array.astype(np.float32) / 127.0 - 1 )

    # Load the image into the array
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    data[0]= normalized_image_array[0:224,0:224,0:3]

    # run the inference
    prediction = model.predict(data)

    max_probability_item_index = np.argmax(prediction[0])


    if prediction.max() > 0.6:
        name = class_dict.get(max_probability_item_index)
        probability = round(prediction[0][max_probability_item_index] * 100, 2)
        mess = MyTextMessage.information(name, probability)                         
        line_bot_api.reply_message(event.reply_token, TextSendMessage(mess))
    else :
        line_bot_api.reply_message(event.reply_token, TextSendMessage("無法辨識您的圖片\n我們感到很抱歉..."))
      

## ==========================
##     影片處理
## ==========================
@handler.add(MessageEvent, VideoMessage)
def handle_vedio(event):
    line_bot_api.reply_message(event.reply_token, TextSendMessage("監修中...敬請期待！\nComing Soon..."))

## ==========================
##     音訊處理
## ==========================
@handler.add(MessageEvent, AudioMessage)
def handle_vedio(event):
    line_bot_api.reply_message(event.reply_token, TextSendMessage("監修中...敬請期待！\nComing Soon..."))

## ==========================
##   運作主程序
## ==========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))