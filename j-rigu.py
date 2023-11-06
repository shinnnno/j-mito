from bs4 import BeautifulSoup
import requests
import pandas as pd
import streamlit as st

st.title('アウェイ水戸ホーリーホック戦')

#フットボールラボのURL
url='https://www.football-lab.jp/gun/report/?year=2023&month=10&date=22'
#URLを取得して読みやすいように変換する
thesp = requests.get(url)
thesp_soup = BeautifulSoup(thesp.text, 'html.parser')
#ホーム、アウェイのチーム名
home_team_name=thesp_soup.find('td',{'class':'tName r'}).text
away_team_name=thesp_soup.find('td',{'tName l'}).text
#ホーム、アウェイのスコア
score=thesp_soup.find_all('td',{'numL c'})
goal_home=score[0].text
goal_away=score[2].text
#ホームスタジアムの名前
space=thesp_soup.find('div',{'class':'boxHalfSP r'})
space=space.text
#試合日と時間
info=thesp_soup.find('div',{'class':'boxHalfSP l'})
info_mito=info.text
#試合の天気、気温、芝の状態、観客の数
weather=thesp_soup.find('div',{'class':'infoList'})
weather2=weather.find_all('dd')
weather_mito=weather2[0].text
temp=weather2[1].text
grass=weather2[2].text
audience=weather2[3].text
#表にまとめる
df_info=pd.DataFrame(
    data={'日付':[info_mito],
          '場所':[space],
          '天気':[weather_mito],
          '気温':[temp],
          '芝':[grass],
          '観客':[audience],
          'ホームチーム':[home_team_name],
          'アウェイチーム':[away_team_name],
          'ホーム得点':[goal_home],
          'アウェイ得点':[goal_away]}
)

#以下スタッツ
time_stats=thesp_soup.find_all('table',{'class':'statsTbl6'})
team_stast=time_stats[1]

#team_stastの中からタグtdを探し出してtd_tagsに代入
td_tags=team_stast.find_all('td')
#statsリストの中にtd_tagsを入れてさらに見やすくした
stats=[]
for td_tags in td_tags:
    stats.append(td_tags.text)

#[3::8]はスライスを使用。最初の数字は開始位置。最後の数字は3+8の11の所で止まる
stats_home_num = stats[3::8] #ホームチームの総数を格納する
stats_home_per = stats[2::8] #ホームチームの成功率を格納する
stats_away_num = stats[5::8] #アウェイチームの総数を格納する
stats_away_per = stats[6::8]
#stats_allの中にstatsをすべて入れてそれを表でまとめた
stats_all=stats_home_num+stats_home_per+stats_away_num+stats_away_per
thesp_stats=pd.DataFrame([stats_all])

stats_columns = stats[0::8] #データ項目名を格納する
#名前にhome, awayをプラスで書いている
#カラム名が格納された配列を作成する
columns = []
#上から順番に書いているからhome,awayがうまく分けられている
for stats_column in stats_columns:
    column_name = str(stats_column) + "_Home"
    columns.append(column_name)
for stats_column in stats_columns:
    column_name = str(stats_column) + "_成功率_Home"
    columns.append(column_name)
for stats_column in stats_columns:
    column_name = str(stats_column) + "_Away"
    columns.append(column_name)
for stats_column in stats_columns:
    column_name = str(stats_column) + "_成功率_Away"
    columns.append(column_name)

#データフレームにカラム名を適用する
thesp_stats.columns = columns
#数字が入力されていない欄を削除する
null_index=[i for i, x in enumerate(stats_all) if x == '-']
df_stats=thesp_stats.drop(thesp_stats.columns[null_index], axis=1)

#スタッツを組み合わせる
df_info_home=pd.DataFrame(
    data={'日付':[info_mito],
          '場所':[space],
          '気温':[temp],
          '観客':[audience],
          'チーム名':[home_team_name],
          '対戦相手':[away_team_name],
          'Home/away':'Hoem',
          '得点':[goal_home],
          '失点':[goal_away]}
)

df_info_away=pd.DataFrame(
    data={'日付':[info_mito],
          '場所':[space],
          '気温':[temp],
          '観客':[audience],
          'チーム名':[away_team_name],
          '対戦相手':[home_team_name],
          'Home/away':'away',
          '得点':[goal_away],
          '失点':[goal_home]}
)

stats_home=stats_home_num+stats_home_per+stats_away_num+stats_away_per
stats_away=stats_away_num+stats_away_per+stats_home_num+stats_home_per

df_stats_home=pd.DataFrame([stats_home])
df_stats_away=pd.DataFrame([stats_away])

stats_columns=stats[0::8]
#列名の変更をしている。８回ずつで区切られている
columns=[]+stats_columns
for stats_column in stats_columns:
    column_name = str(stats_column) + "_成功率"
    columns.append(column_name)
for stats_column in stats_columns:
    column_name = "（被）" + str(stats_column)
    columns.append(column_name)
for stats_column in stats_columns:
    column_name = "（被）" + str(stats_column) + "_成功率"
    columns.append(column_name)
#df_stats_home.columns=columnsと書く理由はcolumnsの列名の変更を使うから
df_stats_home.columns=columns
df_stats_away.columns=columns

#-は何も数値が入っていない列を探し出してnullに格納した
home_null_index=[i for i, x in enumerate(stats_home) if x == '-']
away_null_index=[i for i, x in enumerate(stats_away) if x == '-']
#dropで何も格納されていない列を削除
df_stats_home=df_stats_home.drop(df_stats_home.columns[home_null_index], axis=1)
df_stats_away=df_stats_away.drop(df_stats_away.columns[away_null_index], axis=1)

#スタッツと日時を合体させる
df_match_home=pd.concat([df_info_home,df_stats_home],axis=1)
df_match_away=pd.concat([df_info_away,df_stats_away],axis=1)
#awayとhomeを合体させる
df_match=pd.concat([df_match_home,df_match_away],axis=0)

#戦評
verdict=thesp_soup.find_all('div',{'class':'cpt'})
verdict=verdict[0].text

st.write('''
水戸ホーリーホック データ
''')
st.dataframe(df_match_home)
st.write('''
ザスパクサツ群馬 データ
''')
st.dataframe(df_info_away)
st.write('''
合体
''')
st.dataframe(df_match)
st.write('''
戦評
''')
st.write(verdict)