import json, os
from linebot.models import RichMenu

class MenuRawData:
    # 圖文選單
    menuData = """{
        "size":{"width": 2500, "height": 1686},
        "selected": "True", 
        "name": "查看更多資訊",
        "chatBarText": "查看更多資訊",
        "areas":[{
            "bounds": {"x": 0, "y": 0, "width": 2500, "height": 850},
            "action": {"type": "postback","data": "最新消息"}
            },{
            "bounds": {"x": 0, "y": 843, "width": 833, "height": 843},
            "action": {"type": "postback","data": "!pb"}
            },{
            "bounds": {"x": 833, "y": 843, "width": 834, "height": 843},
            "action": {"type": "postback","data": "前往商店"}
            },{
            "bounds": {"x": 1667, "y": 843, "width": 833, "height": 843},
            "action": {"type": "postback", "data": "指令"}
            }]
    }"""
    @classmethod
    def line_menu(cls, line_bot_api):
        # 讀取圖文選單設定檔
        menuJson = json.loads(cls.menuData)
        # 創造圖文選單 id (new_from_json_dict 可以從 json 裡面生成 RichMenu 物件)
        lineRichMenuId = line_bot_api.create_rich_menu(
            rich_menu = RichMenu.new_from_json_dict(menuJson)
        )
        return lineRichMenuId
    

class MyTextMessage:
    follow_text= "歡迎你的加入！\n\n你可以在遇到不認識的角色時，上傳一張圖片，我們會幫你找到答案，不管是電影、動畫、遊戲、VTuber等都可以試試看。\n(目前辨識模型大約有10個左右的火影忍者的角色。功能擴建中...)\n\nP.S.您所提供的圖片將會加入我們的資料庫，以提升辨識的準確度"
    say_hollo = {"你好", "Hollo", "安安", "こんにちは", "もしもし", "嗨嗨", "Hi", "안녕하세요", "ON LI DAY FaOHE MASHI", "BONJOUR", "幹"}

    postback_data = {
        "最新消息":"最新消息：\n活動籌備中！！\nComing Soon...",
        "角色測驗":"角色測驗：\n設計中！！\nComing Soon...",
        "前往商店":"商店籌備中！！\nComing Soon...",
        "指令":"指令：\n1.圖片辨識：直接上傳圖片\n2.特徵辨識：開頭加上「!」\n3.尋求幫助：@more"
    }   

    @classmethod
    def information(cls, name, probability):
        return f"這個角色可能為 「{name}」\n相似機率為 {probability}%\n\n角色簡介：Coming Soon...\n官方粉絲團：https://reurl.cc/AA4jle\n最新活動：Coming Soon...\n周邊購買：Coming Soon..."


class ModelLabels:
    @classmethod
    def labels_text(cls):
        labels_dic = []
        with open('converted_savedmodel/labels.txt', "r", encoding="utf-8") as file:
            for d in file:
                key, val = d.split()
                labels_dic.append(val)
        return labels_dic

