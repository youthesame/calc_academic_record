from copy import deepcopy

import pandas as pd
import plotly.express as px
import streamlit as st

usecols = ["科目大区分", "科目中区分", "科目", "単位数", "修得年度", "修得学期", "評価", "評語", "合否"]

st.write("[GitHub](https://github.com/youthesame/calc_academic_record.git)")
uploaded_file = st.file_uploader(
    "学務情報システムからダウンロードした 「kakuteiSeisekiCsv.csv」 を選択してください", type="csv"
)
st.write("動作しない場合は [こちら](https://forms.gle/SBvfQuE7kAiLGMULA)")

if uploaded_file is not None:
    try:
        _df = pd.read_csv(uploaded_file, header=3, usecols=usecols, encoding="cp932")
    except ValueError:
        st.error("**アップロードされたファイルは処理できません。**もう一度、学務情報システムから成績をダウンロードしてください。")
    str_replace = {"Ｓ": 4, "Ａ": 3, "Ｂ": 2, "Ｃ": 1, "Ｆ": 0, "否": 0, "合": 1}
    df = _df.replace(str_replace)
    df["点数"] = df["単位数"] * df["評語"] * df["合否"]

    gps = df["点数"].sum()
    gpa = gps / df["単位数"].sum()

    # 年度別ヒストグラムの作成
    df["修得年度"] = df["修得年度"].astype(str)
    fig = px.histogram(
        df,
        x="修得年度",
        y="点数",
        color="修得学期",
        labels={"修得学期": "学期", "修得年度": "年度", "点数": "grade point"},
    )
    fig.update_xaxes(title="年度")
    fig.update_yaxes(title="GPS")

    # GPS･GPAの詳細
    df["修得年度"] = df["修得年度"].astype(int)
    year_list0 = df["修得年度"].unique().tolist()
    ylen = len(year_list0)
    year_list = deepcopy(year_list0)
    year_list.extend(year_list0)
    year_list.sort()
    semester_list0 = ["前期", "後期"]
    semester_list = []
    for _ in range(ylen):
        semester_list.extend(semester_list0)

    data = pd.DataFrame()
    count = 0
    for year in year_list0:
        for semester in semester_list0:
            tmp_df = df[(df["修得年度"] == year) & (df["修得学期"] == semester)]
            tmp_gps = tmp_df["点数"].sum()
            data.at[f"{count}", "GPS"] = tmp_gps
            data.at[f"{count}", "GPA"] = tmp_gps / tmp_df["単位数"].sum()
            count += 1

    ndata = data.values
    record_df = pd.DataFrame(
        data=ndata, index=([year_list, semester_list]), columns=data.columns
    )
    record_df["GPS"] = record_df["GPS"].astype(int)
    record_df.loc["Total", :] = [gps, gpa]

    eval_series = _df["評語"].value_counts()
    eval_series.name = "取得数"

    subject_series = pd.Series(dtype="int64")
    sbject_list = df["科目中区分"].unique().tolist()
    for subject in sbject_list:
        a = df[(df["科目中区分"] == subject) & (df["合否"] == 1)]
        subject_series[subject] = a["単位数"].sum()
    subject_series["Total"] = subject_series.sum()
    subject_series.name = "取得単位数"

    # streamlitで表示
    st.header("成績表")
    st.table(record_df)
    st.header("成績推移")
    st.plotly_chart(fig, use_container_width=True)
    st.header("評価数")
    st.table(eval_series)
    st.header("科目別単位数")
    st.table(subject_series)
    st.header("詳細")
    st.dataframe(_df)
