# pages/batch_process.py
import streamlit as st
from services.text_extraction import extract_text_from_pdf, extract_text_from_url
from services.keyword_count import count_keywords
from services.create_bar_chart import create_bar_chart
import pandas as pd
from pdfminer.high_level import extract_text
import requests
from bs4 import BeautifulSoup
import plotly.express as px

def app():
    # タイトルの設定
    st.title("一括でサステナ単語をカウント")
    # st.sidebar.divider()
    # st.sidebar.markdown("### :orange[「サステナ単語」の分類の選択]")  # サイドバーに分類の選択を追加

    st.subheader('🍀Step1. 分類1~4単語・倍率・段階設定')
    # CSVファイルのアップロード例を表示
    example_data = {
        "分類1": ["価値創造モデル", "価値創造モデル"],
        "分類2": ["価値創造モデル", "価値創造モデル"],
        "分類3": ["価値創造モデル", "価値創造モデル"],
        "分類4": ["価値創造", "価値創造ストーリー"]
    }
    example_df = pd.DataFrame(example_data)
    st.markdown("アップロードするCSVの例:")
    st.dataframe(example_df)
    st.text("... (この下にも行が続く)")
    st.text("")

    uploaded_csv = st.file_uploader("分類1~4のサステナ単語を整理したCSVファイルをアップロードしてください", type=["csv"])
    if uploaded_csv is not None:
        st.success('CSVファイルの読み込みに成功しました!')
        df = pd.read_csv(uploaded_csv)
        df.columns = df.columns.str.strip()

        # ファイルタイプの選択
        st.sidebar.divider()
        st.sidebar.markdown("### :orange[ファイルのタイプ選択]")  # サイドバーに分類の選択を追加
        file_type = st.sidebar.radio("今回の評価対象のファイルタイプを選択してください：", ("PDF", "Webリンク"))

        # ドキュメント入力
        st.divider()
        st.subheader('🍀Step2. 評価対象の設定')
        text = ""
        
        if file_type == "PDF":
            uploaded_file = st.file_uploader("今回の評価対象のPDFファイルをアップロードしてください", type=["pdf"])
            if uploaded_file is not None:
                st.success('PDFの読み込みに成功しました!')
                text = extract_text(uploaded_file)
                uploaded_file_name = uploaded_file.name  # アップロードされたPDFファイルの名前を取得
            else:
                uploaded_file_name = ""
        else:
            url = st.text_input("WebページのURLを入力してください")
            if url:
                st.success('URLの読み込みに成功しました!')
                text = extract_text_from_url(url)
        st.caption('PDF等の読み込みに時間を要します。')
        st.caption('下記ボタン「カウント」を押すまでに5~10秒ほどお待ちいただくことがございます。')

        st.divider()
        st.subheader('🍀Step3. 単語出現回数カウント')
        if st.button("🚀単語出現回数カウント処理を実行🚀"):
            keywords = df['分類4'].unique()
            with st.spinner('処理中...'):
                # filtered_df = df[df['分類1'] == option1]
                total_rows = len(df)
                result_data = []

                for _, row in df.iterrows():
                    keyword = row['分類4']
                    count = text.lower().count(keyword.lower())
                    # countが0の時はnew_stageも0にする
                    if count > 0:
                        new_stage = count // 10 + 1  # 10回につき段階が1Up
                    else:
                        new_stage = 0
                    # score = row['段階'] * row['倍率'] * count
                    # スコアを含めてresult_dataに追加
                    result_data.append([row['分類1'], row['分類2'], row['分類3'], row['分類4'], count, new_stage])
                # スコアを含む新しいDataFrameを作成
                score_df = pd.DataFrame(result_data, columns=['分類1', '分類2', '分類3', '分類4', '単語出現回数', '段階'])
                # st.markdown("スコア = 倍率 × 段階")
                st.dataframe(score_df.style.bar(subset=['単語出現回数'], vmin=0, vmax=10, color='#5fba7d'))
                
            st.success('処理完了！')

            # CSV出力機能
            st.divider()
            st.subheader('🍀Step4. CSVダウンロード')
            csv = score_df.to_csv(index=False).encode('utf-8')
            file_name_prefix = uploaded_file_name.split('.')[0] if uploaded_file_name else "evaluation"  # 拡張子を除いたファイル名を使用
            file_name = f"{file_name_prefix}-all-evaluation.csv"
            st.download_button(
                label="結果をCSVでダウンロード",
                data=csv,
                file_name=file_name,
                mime="text/csv",
            )

# 棒グラフ作成関数 (create_bar_chart) の修正版
def create_bar_chart(df, x, y, title):
    fig = px.bar(df, x=x, y=y, title=title, orientation='h')
    fig.update_layout(xaxis_title="段階", yaxis_title="分類", 
                    xaxis={'categoryorder':'total descending'}, height=1000)
    return fig 

if __name__ == "__main__":
    app()