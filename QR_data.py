from linebot.models import QuickReply, QuickReplyButton, MessageAction, PostbackAction, TextSendMessage, TextMessage
from linebot import LineBotApi
from message_data import ModelLabels
from random import randint
import os

# QuickReply Button
class QRB:
    line_bot_api = LineBotApi(channel_access_token=os.environ["LINE_CHANNEL_ACCESS_TOKEN"])
    total_user = {}   # 儲存每個使用者的目前分數(應該要存到 firestore) 

    QA = [
        ["1.你的性格屬於哪一類型?","熱血型", "細心型", "冷酷型", "天真型", "結束做答"],
        ["2.你最喜歡的休閒活動是什麼?","戶外運動", "閱讀書籍", "藝術創作", "觀賞電影", "結束做答"],
        ["3.你覺得自己的最大優勢是什麼?","智力","溫柔", "堅毅","冷靜", "結束做答"],
        ["4.如果給你一個機會可以學習一項新技能，你最想學習的是什麼？","音樂樂器", "繪畫", "烹飪", "衝浪", "結束做答"],
        ["5.你喜歡跟人合作還是獨立工作？","跟人合作", "獨立工作", "都可以，視情況而定", "不確定", "結束做答"],
        ["6.在解決問題時，你通常會採取什麼方式？","分析問題","試錯法", "聽取建議", "直覺", "結束做答"],
        ["7.你喜歡嘗試新事物嗎？","是的","有時候","不太喜歡","不確定", "結束做答"],
        ["8.你通常是如何安排自己的時間？","按表操課","靈活應變","隨遇而安","常常會拖延", "結束做答"],
        ["9.你喜歡與不同背景的人交流嗎？","是的","不喜歡","不確定","取決於對方的個性", "結束做答"],
        ["10.在壓力下，你通常的應對方式是什麼？","冷靜應對", "尋求他人", "運動或娛樂", "自爆", "結束做答"]
    ]
    @classmethod
    def qrb(cls, event):
        user_profile = cls.line_bot_api.get_profile(event.source.user_id)
        epd = event.postback.data[-1]  
        if epd == "b":
            cls.total_user[user_profile.user_id] = [0, 0]  # [index, count]                 
        elif epd in {"1","2","3","4"}:
            cls.total_user[user_profile.user_id][1] += int(epd)

        ind = cls.total_user[user_profile.user_id][0]
        count = cls.total_user[user_profile.user_id][1]  
            
        if epd == "5":
            del cls.total_user[user_profile.user_id]
            return TextSendMessage(text="角色測驗中止！")
        elif cls.total_user[user_profile.user_id][0] == 10:
            role = ModelLabels.labels_text()
            role_len = len(role)
            r = randint(role_len, role_len+100)
            one = role[(count+r)%(role_len+1)]
            del cls.total_user[user_profile.user_id]
            return TextSendMessage(text=f"「 {one} 」\n\n！！目前為隨機產生！！\n！！將會再做調整！！")
         
      

        pb1 = QuickReplyButton(action = PostbackAction(label=cls.QA[ind][1], text=cls.QA[ind][1], data="!pb1" ))
        pb2 = QuickReplyButton(action = PostbackAction(label=cls.QA[ind][2], text=cls.QA[ind][2], data="!pb2" ))
        pb3 = QuickReplyButton(action = PostbackAction(label=cls.QA[ind][3], text=cls.QA[ind][3], data="!pb3" ))
        pb4 = QuickReplyButton(action = PostbackAction(label=cls.QA[ind][4], text=cls.QA[ind][4], data="!pb4" ))
        pb5 = QuickReplyButton(action = PostbackAction(label=cls.QA[ind][5], text=cls.QA[ind][5], data="!pb5" ))
        
        all_Button = [pb1,pb2,pb3,pb4,pb5]
        QR_List = QuickReply(items = all_Button)
        if epd == "b":
            quick_reply_text_send_message = TextSendMessage(text=f"【角色測驗】開始：\n(如果中途跳掉，請再按一次繼續回答)\n\n{cls.QA[ind][0]}", quick_reply=QR_List)
        else:
            quick_reply_text_send_message = TextSendMessage(text=cls.QA[ind][0], quick_reply=QR_List)
        cls.total_user[user_profile.user_id][0] += 1
        return quick_reply_text_send_message

