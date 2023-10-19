import os
import opencc
import openai
import pandas as pd
from tqdm import tqdm
from tabulate import tabulate

def messeage_prepare(system_info, prompt_info):
        message = [
            {"role": "system", "content": system_info},
            {"role": "user", "content": prompt_info}
            ]
        return message

def print_and_save_qka_chatgpt(question_list, docs_and_scores_list, n=3, k=4, threshold=0.8, model="gpt-3.5-turbo",csv_saved_path='data/langchain_chatgpt.csv'):
    qka_dataframe = {
        "Question":[],
        "Knowledge":[],
        "Answer":[],
    }

    if os.path.exists(csv_saved_path):
        df = pd.read_csv(csv_saved_path)
        question_list = question_list[len(df):]
        docs_and_scores_list = docs_and_scores_list[len(df):]
        qka_dataframe = df.to_dict('list')

    system_info = "你是聊天機器人 Retrieval Bot, [檢索資料]是由 Ruby Lin 提供的。 參考[檢索資料]使用中文簡潔和專業的回覆顧客的[問題], 如果答案不在公開資料中, 請說 “對不起, 我所擁有的資料中沒有相關資訊, 請您換個問題或將問題描述得更詳細, 讓我能正確完整的回答您”\n\n"
    s2t = opencc.OpenCC('s2t.json')

    tabulate_format = []
    for idx in tqdm(range(len(question_list))):
        ## Print table
        question = question_list[idx]
        knowledge = []
        for i in range(k):
            docs, score = docs_and_scores_list[idx][i]
            if score > threshold:
                knowledge.append(docs.page_content)
            else:
                break
        if knowledge == []:
            knowledge.append("無法獲取答案")

        knowledge = "\n".join(knowledge)
        prompt_info = "[檢索資料]" + "\n" + knowledge + "\n\n" + "[問題]" + "\n" + question

        response = openai.ChatCompletion.create(
            model=model,
            messages=messeage_prepare(system_info, prompt_info),
            temperature=0.1,
        )
        answer = s2t.convert(response["choices"][0]["message"]["content"])

        ## Save values
        tabulate_format.append([question, knowledge , answer])
        qka_dataframe['Question'].append(question)
        qka_dataframe['Knowledge'].append(knowledge)
        qka_dataframe['Answer'].append(answer)

        if (idx+1) % n == 0:
                print(tabulate(tabulate_format, ["Question"] + ["Knowledge"] + ["Answer"], tablefmt='fancy_grid', maxcolwidths=40))
                tabulate_format = []
                filter_config = {
                                    "Answer":{
                                        r'根據.*?，':"",
                                        r'我所擁有的公開資料':"我本次檢索的資料",
                                        r'\[公開資料\]':"公開資料",
                                        r'公開資料':"網路上的公開資料",
                                    }
                                }
                pd.DataFrame(qka_dataframe).replace(filter_config, regex=True).to_csv(csv_saved_path, header=True, index=False, encoding="utf_8_sig")

