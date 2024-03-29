# pages/batch_process.py
import streamlit as st
from services.create_bar_chart import create_bar_chart
import pandas as pd
from pdfminer.high_level import extract_text
import requests
from bs4 import BeautifulSoup
import plotly.express as px
from io import BytesIO
import zipfile

def app():
    # タイトルの設定
    st.title("サステナスコアをグラフ描写")
    if 'step2_completed' not in st.session_state:
        st.session_state['step2_completed'] = False  # Step2が完了したかどうかのフラグを初期化

    st.subheader('🍀Step1. 分類1~4単語・倍率・段階設定')
    uploaded_csv = st.file_uploader("分類1~4のサステナ単語を整理したCSVファイルをアップロードしてください", type=["csv"])
    # CSVファイルのアップロード例を表示
    example_data = {
        "分類1": ["価値創造モデル", "価値創造モデル"],
        "分類2": ["価値創造モデル", "価値創造モデル"],
        "分類3": ["価値創造モデル", "価値創造モデル"],
        "分類4": ["価値創造", "価値創造ストーリー"],
        "倍率": [1, 3],
        "段階": [1, 0]
    }
    example_df = pd.DataFrame(example_data)
    st.markdown("アップロードするCSVの例:")
    st.dataframe(example_df)
    st.text("... (この下にも行が続く)")
    st.text("")
    if uploaded_csv is not None:
        st.success('CSVファイルの読み込みに成功しました!')
        df = pd.read_csv(uploaded_csv)
        df.columns = df.columns.str.strip()

        # アップロード成功時に状態を保持
        st.session_state.uploaded = True

        st.divider()
        st.subheader('🍀Step2. グラフ描写')
        if st.button("🚀グラフを描写🚀"):
            keywords = df['分類4'].unique()
            with st.spinner('処理中...'):
                # filtered_df = df[df['分類1'] == option1]
                total_rows = len(df)
                result_data = []

                for _, row in df.iterrows():
                    keyword = row['分類4']
                    # スコアの計算（段階 × 倍率 × 単語出現回数）
                    score = row['段階'] * row['倍率']
                    # スコアを含めてresult_dataに追加
                    result_data.append([row['分類1'], row['分類2'], row['分類3'], row['分類4'], score])
                # スコアを含む新しいDataFrameを作成
                score_df = pd.DataFrame(result_data, columns=['分類1', '分類2', '分類3', '分類4', 'スコア'])
                st.markdown("### スコアの算定式")
                st.markdown("| スコア = 段階 × 倍率")
                # st.dataframe(score_df.style.bar(subset=['スコア'], vmin=0, vmax=10, color='#5fba7d'))
                
                # 分類3ごとのスコアを集計
                score_by_cat3 = score_df.groupby(['分類1', '分類2', '分類3'])['スコア'].sum().reset_index()

                # 分類2ごとのスコアを集計
                score_by_cat2 = score_by_cat3.groupby(['分類1', '分類2'])['スコア'].sum().reset_index()

                # 分類1ごとのスコアを集計
                score_by_cat1 = score_by_cat2.groupby(['分類1'])['スコア'].sum().reset_index()

                # 分類1の粒度で棒グラフを表示
                fig_cat1 = create_bar_chart(score_by_cat1, x='スコア', y='分類1', title='分類1ごとのスコア')
                st.plotly_chart(fig_cat1)

                # 分類2の粒度で棒グラフを表示
                fig_cat2 = create_bar_chart(score_by_cat2, x='スコア', y='分類2', title='分類2ごとのスコア')
                st.plotly_chart(fig_cat2)

                # 棒グラフの作成と表示 (分類3の粒度)
                fig_cat3 = create_bar_chart(score_by_cat3, x='スコア', y='分類3', title='分類3ごとのスコア')
                st.plotly_chart(fig_cat3)
            st.success('処理完了！')

            # ZIPファイルを作成
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
                zip_file.writestr('分類1_スコア.csv', to_csv(score_by_cat1))
                zip_file.writestr('分類2_スコア.csv', to_csv(score_by_cat2))
                zip_file.writestr('分類3_スコア.csv', to_csv(score_by_cat3))
            
            # ZIPファイルをダウンロードボタンに設定
            zip_buffer.seek(0)
            st.download_button(
                label="全スコア結果をZIPでダウンロード",
                data=zip_buffer,
                file_name="スコア結果.zip",
                mime="application/zip"
            )

# 棒グラフ作成関数 (create_bar_chart) の修正版
def create_bar_chart(df, x, y, title):
    fig = px.bar(df, x=x, y=y, title=title, orientation='h')
    fig.update_layout(xaxis_title="スコア", yaxis_title="分類", 
                    xaxis={'categoryorder':'total descending'}, height=1000)
    return fig 

# CSVファイルをメモリに書き込む関数
def to_csv(df):
    buffer = BytesIO()
    df.to_csv(buffer, index=False, encoding='utf-8-sig')
    buffer.seek(0)
    return buffer.getvalue()

if __name__ == "__main__":
    app()
