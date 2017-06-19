# -*- coding: utf-8 -*-

import datetime
import random
import re
import time
import tweepy

from izumin import key        # 本番環境ではこちら
# from izumin import key_local  # ローカルではこちら
from izumin import math


class Twitter:
    """Twitterクラス"""

    def __init__(self):
        # ローカルでテストする際はkeyをコメントアウトし、key_localのコメントを外す。
        self.auth = tweepy.OAuthHandler(key.CONSUMER_KEY, key.CONSUMER_SECRET)
        self.auth.set_access_token(key.ACCESS_TOKEN, key.ACCESS_SECRET)
        # self.auth = tweepy.OAuthHandler(key_local.CONSUMER_KEY, key_local.CONSUMER_SECRET)
        # self.auth.set_access_token(key_local.ACCESS_TOKEN, key_local.ACCESS_SECRET)
        self.api = tweepy.API(self.auth)
        self.previous_reply_id = self.api.mentions_timeline(count=1)[0].id
        print("Set previous reply id: ", self.previous_reply_id)

    def user_timeline(self):
        """直近の自分のツイート最大20件を取得し、リスト形式で返す。"""

        user_timeline_status = self.api.user_timeline()
        recently_tweet_num = len(user_timeline_status)  # 直近ツイート件数（基本は20件だが、ツイート数が20未満の場合はその数になる）

        # 直近のツイートをリスト形式にする。
        recently_tweet_list = []
        i = 0
        while i < recently_tweet_num:
            recently_tweet = user_timeline_status[i].text
            recently_tweet_list.append(recently_tweet)
            i = i + 1

        return recently_tweet_list

    def select_tweet_random(self):
        """ツイートリストの中からランダムで1つ選んで返す。"""

        # main.pyからimportされた場合とコマンドラインから直接実行された場合で、
        # ツイートリストの相対パスが違うのでここで設定する。
        if __name__ == '__main__':
            tweet_file = "../Contents/tweet_list.txt"
        else:
            tweet_file = "Contents/tweet_list.txt"

        # tweet_list.txtを読み込む。
        f = open(tweet_file, 'r', encoding="utf_8_sig")
        tweet_file_data = f.read()
        f.close()

        # ファイルから必要なデータのみ取り出す。
        tweet_list_including_garbage = tweet_file_data.split('"')
        tweet_list = list(filter(lambda s: s != '' and s != '\n', tweet_list_including_garbage))

        # 直近のツイート最大20件を取得する。
        recently_tweet_list = self.user_timeline()

        random.seed()
        is_tweet_decision = False  # 何をツイートするか決定したかどうかのフラグ
        while not is_tweet_decision:
            # tweet_listの中からランダムにツイートを選択する。
            tweet_candidate = random.choice(tweet_list)

            # 同じ内容のツイートをしていないか、確認する。
            i = 0
            recently_tweet_num = len(recently_tweet_list)
            while i < recently_tweet_num:
                if recently_tweet_list[i] == tweet_candidate:
                    # 直近のツイートに今回のツイート候補が入っていたら選び直す。
                    break
                i = i + 1
            else:
                is_tweet_decision = True

        return tweet_candidate

    def update(self, new_tweet, reply_id=None):
        """new_tweetを投稿する。"""

        # ツイートする。
        try:
            self.api.update_status(status=new_tweet, in_reply_to_status_id=reply_id)
            if reply_id is None:
                print("Tweet succeeded")
            else:
                print("Reply succeeded")
        except tweepy.TweepError as e:
            print(e.reason)

    def reply_check(self):
        """リプライに反応する。"""

        # 前回からのリプライをすべて取得する。
        mentions_statuses = self.api.mentions_timeline(since_id=self.previous_reply_id)

        # リプライに1つずつ対応する。
        for mention in mentions_statuses:
            mention_id = mention.id  # リプライ先のツイートID
            mention_name = mention.author.screen_name  # リプライ相手のスクリーンネーム
            mention_text = mention.text.split(' ')
            self.previous_reply_id = mention_id  # 前回リプライのIDを更新

            print("Received reply, id: ", mention_id)
            print("Mention Name: ", mention_name)
            print("Message is 「", mention.text, "」")

            completed_reply = False
            for text in mention_text:  # 送られてきたリプライを空白区切りで処理する。
                if text[0] == "@":
                    pass
                else:  # 数字のみ取り出す
                    num_candidate_list = re.split("\D+", text)
                    for num_candidate in num_candidate_list:
                        if num_candidate.isdigit():  # 空文字列が入っている可能性があるためチェックする。
                            num = int(num_candidate)
                            reply_text = self.number_reply("@" + mention_name + " ", num)
                            self.update(reply_text, reply_id=mention_id)
                            completed_reply = True
            else:
                if not completed_reply:
                    print("Not reply")

    @staticmethod
    def number_reply(screen_name, number):
        """数字を判定してメッセージを返す。"""

        if len(str(number)) > 15:
            reply = screen_name + "ごめんね。ちょっとわからないな。"
        elif math.is_perfect_number(number):
            reply = screen_name + str(number) + "は完全数だね。すっごーい！"
        elif number is 57:
            reply = screen_name + "ふふっ、" + str(number) + "はグロタンディーク素数ね。"
        elif math.is_prime(number):
            reply = screen_name + str(number) + "は素数ね。"
        else:
            reply = screen_name + str(number) + "は素数じゃないよ。"
        return reply

    @staticmethod
    def prime_message():
        """毎日0:00にツイートするその日の素数情報メッセージ"""

        today = datetime.date.today()
        # 西暦を文字列にして格納
        today_str = str(today.year)

        # 月を文字列にして連結
        if len(str(today.month)) < 2:
            today_str = today_str + "0"
        today_str = today_str + str(today.month)

        # 日を文字列にして連結
        if len(str(today.day)) < 2:
            today_str = today_str + "0"
        today_str = today_str + str(today.day)
        today_number = int(today_str)  # 数値化

        status = "よるほー。大石泉が0時をお知らせするよ。\n今日の日付、\""
        if math.is_prime(today_number):
            status = status + str(today_number) + "\"は素数ね。"
        else:
            status = status + str(today_number) + "\"は素数じゃないわね。"
        return status


if __name__ == '__main__':
    twitter = Twitter()
    while True:
        twitter.reply_check()
        time.sleep(60)
