import streamlit as st
import pandas as pd
from pdfminer.high_level import extract_text
from datetime import datetime
import pytz
import os
import requests

def app():
    st.title("一括でサステナ単語をカウント")
    # セッション状態でのurlsの初期化
    if 'urls' not in st.session_state:
        st.session_state.urls = []

    # スクリプトのあるディレクトリの絶対パスを取得
    dir_path = os.path.dirname(os.path.realpath(__file__))
    parent_dir = os.path.dirname(dir_path)
    default_csv_path = os.path.join(parent_dir, 'kw-hierarchy_20240326.csv')

    st.subheader('🍀Step1. 分類1~4単語・倍率・段階設定')

    # CSV選択オプションをプルダウンから選択
    csv_option = st.selectbox("CSVファイルを選択してください:",
                                options=["", '「kw-hierarchy_20240326.csv」を利用する', '分類1~4を整理した新規CSVを利用する'],
                                index=0,
                                format_func=lambda x: x if x else "選択してください...")

    # 「kw-hierarchy_20240326.csv」を利用する選択肢が選ばれた場合
    if csv_option == '「kw-hierarchy_20240326.csv」を利用する':
        # デフォルトCSVの読み込み
        load_default_csv(default_csv_path)
        proceed_to_step2()
    
    # 新規CSVを利用する選択肢が選ばれた場合
    elif csv_option == '分類1~4を整理した新規CSVを利用する':
        upload_new_csv()

def load_default_csv(default_csv_path):
    if 'df' not in st.session_state or 'uploaded_file_info' not in st.session_state:
        st.session_state.df = pd.read_csv(default_csv_path)
        st.session_state.uploaded_file_info = 'デフォルトCSVが読み込まれました'

def upload_new_csv():
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
        st.success('新規CSVの読み込みに成功しました！Step2に進みます')
        st.session_state.df = pd.read_csv(uploaded_csv)
        st.session_state.df.columns = st.session_state.df.columns.str.strip()
        st.session_state.uploaded_file_info = uploaded_csv.name + ' がアップロードされました'
        proceed_to_step2()

def proceed_to_step2():
    # ファイルタイプの選択
    st.sidebar.divider()
    st.sidebar.markdown("### :orange[ファイルのタイプ選択]")  # サイドバーに分類の選択を追加
    file_type = st.sidebar.radio("今回の評価対象のファイルタイプを選択してください：", ("PDF", "Webリンク"))
    st.session_state.file_type = file_type  # ファイルタイプをセッション状態に保存

    # ファイルタイプに応じた処理の実行
    if st.session_state.file_type == "PDF":
        process_pdf(st.session_state.df)
    elif st.session_state.file_type == "Webリンク":
        process_urls(st.session_state.df)

def update_file_type():
    # ファイルタイプの変更を検知するためのダミー関数（必要に応じて実装）
    pass

def process_file_type(df, file_type):
    if file_type == "PDF":
        process_pdf(df)
    else:
        process_urls(df)

def process_pdf(df):
    st.divider()
    st.subheader('🍀Step2. 評価対象の設定')
    uploaded_file = st.file_uploader("今回の評価対象のPDFファイルをアップロードしてください", type=["pdf"])
    if uploaded_file is not None:
        text = extract_text(uploaded_file)
        uploaded_file_name = uploaded_file.name
        # uploaded_fileを引数として渡す
        your_pdf_processing_function(df, uploaded_file, text, uploaded_file_name)

def process_urls(df):
    st.divider()
    st.subheader('🍀Step2. 評価対象の設定')
    number_of_urls = st.selectbox('URLの数を選択してください', range(1, 6), format_func=lambda x: f"{x} 個")
    # 選択した数だけテキスト入力欄を表示
    urls = []
    for i in range(number_of_urls):
        url = st.text_input(f"URL {i+1}", key=f"url_{i}")
        if url:  # URLが入力されている場合のみリストに追加
            urls.append(url)
    st.divider()
    st.subheader('🍀Step3. 単語出現回数カウント')
    all_texts = []
    # 空でないURLのみを処理
    valid_urls = [url for url in urls if url.strip()]
    for url in valid_urls:
        try:
            text = extract_text_from_url(url)
            all_texts.append(text)
        except requests.exceptions.RequestException as e:
            st.error(f"URL '{url}' の読み込みに失敗しました。エラー: {e}")

    if st.button("🚀単語出現回数カウント処理を実行🚀"):
        # URLリストをセッションステートに保存
        st.session_state.urls = urls
        all_texts = [extract_text_from_url(url) for url in urls if url.strip()]
        your_urls_processing_function(df, all_texts, urls)

def your_pdf_processing_function(df, uploaded_file, text, uploaded_file_name):
    # ここでuploaded_fileを使用する必要がある処理を記述
    if uploaded_file is not None:
        # PDFの読み込み成功メッセージ等
        st.success('PDFの読み込みに成功しました！Step3に進みます')
        text = extract_text(uploaded_file)
        uploaded_file_name = uploaded_file.name  # アップロードされたPDFファイルの名前を取得
    else:
        uploaded_file_name = ""
    
    st.caption('PDF等の読み込みに時間を要します。')
    st.caption('下記ボタン「カウント」を押すまでに5~10秒ほどお待ちいただくことがございます。')

    st.divider()
    st.subheader('🍀Step3. 単語出現回数カウント')
    if st.button("🚀単語出現回数カウント処理を実行🚀"):
        keywords = df['分類4'].unique()
        with st.spinner('処理中...'):

            # 各分類4の単語の出現回数を集計
            df['単語出現回数'] = df['分類4'].apply(lambda x: text.lower().count(x.lower()))
            
            # 分類3ごとの単語出現回数の合計を計算
            df_grouped = df.groupby('分類3').agg({'単語出現回数': 'sum'}).reset_index().rename(columns={'count': 'count_category3'})
            
            # 分類3ごとの合計に基づいて新しい段階（new_stage）を計算
            df_grouped['段階'] = df_grouped['単語出現回数'].apply(lambda x: x // 10 + 1 if x > 0 else 0)
            
            # 新しい段階を元のDataFrameに結合
            df_final = pd.merge(df, df_grouped[['分類3', '段階']], on='分類3', how='left')

            display_final_dataframe(df_final)
            download_buttons(df_final, uploaded_file_name)

def your_urls_processing_function(df, all_texts, urls):
    all_counts = []
    # 各URLに対して処理を実行
    for i, text in enumerate(all_texts):  # URLリストの代わりにテキストリストを使用
        # URLごとのカウント列名
        count_col_name = f'単語出現回数_URL_{i+1}'
        # 各キーワードの出現回数をカウント
        df[count_col_name] = df['分類4'].apply(lambda x: text.lower().count(x.lower()))
        all_counts.append(count_col_name)
    
    # 各URLの単語出現回数を集計して合計を計算
    df['単語出現回数（合計）'] = df[all_counts].sum(axis=1)

    # URLに対応するラベルを生成し、単語出現回数（個別）の文字列を更新
    df['単語出現回数（個別）'] = df.apply(lambda x: ', '.join([f"URL {i+1}({x[col]})" for i, col in enumerate(all_counts) if x[col] > 0]), axis=1)
    
    # 分類3ごとに単語出現回数の合計を計算
    df_grouped = df.groupby('分類3')['単語出現回数（合計）'].sum().reset_index()
    df_grouped.rename(columns={'単語出現回数（合計）': 'count_category3'}, inplace=True)

    # 分類3ごとの合計に基づいて新しい段階を計算
    df_grouped['段階'] = df_grouped['count_category3'].apply(lambda x: max(1, x // 10 + 1) if x > 0 else 0)

    # 新しい段階をもとのDataFrameに結合
    df_final = pd.merge(df, df_grouped[['分類3', '段階']], on='分類3', how='left')

    # 結果の表示とダウンロードボタンの配置
    display_final_dataframe(df_final, is_url=True)
    download_buttons(df_final, "evaluation_URLs")

def download_buttons(df, file_name_prefix):
    # 不要な列（単語出現回数_URL_x）を削除するための処理
    columns_to_remove = [col for col in df.columns if col.startswith('単語出現回数_URL_')]
    df_cleaned = df.drop(columns=columns_to_remove)

    # CSVファイルのダウンロードボタン
    csv = df_cleaned.to_csv(index=False).encode('utf-8')
    jst = pytz.timezone('Asia/Tokyo')
    now = datetime.now(jst).strftime('%Y%m%d%H%M%S')
    file_name = f"{file_name_prefix}-{now}.csv"
    st.download_button("結果をCSVでダウンロード", csv, file_name=file_name, mime="text/csv")
    
    # URLリストが存在する場合
    if 'urls' in st.session_state and st.session_state.urls and st.session_state.file_type == "Webリンク":
        urls = st.session_state.urls
        url_text = "\n".join([f"URL {i+1}\n{url}" for i, url in enumerate(urls)])
        txt_file_name = f"{file_name_prefix}_{now}.txt"
        st.download_button("URLリストをTXTファイルとしてダウンロード", url_text.encode('utf-8'), file_name=txt_file_name, mime="text/plain")

def create_txt_download(file_name_prefix, urls):
    # 現在の日時を日本時間で取得し、YYYYMMDDHHMMSS形式でフォーマット
    jst = pytz.timezone('Asia/Tokyo')
    now = datetime.now(jst).strftime('%Y%m%d%H%M%S')
    
    # ファイル名を生成（ファイル名のプレフィックスにタイムスタンプを含む）
    txt_file_name = f"{file_name_prefix}_URL_{now}.txt"
    
    # URLテキストを生成（各URLの前にその番号を表示）
    url_text = "\n".join([f"URL {i+1}\n{url}" for i, url in enumerate(urls)])
    
    # ダウンロードボタンを配置
    st.download_button(
        label="URLリストをTXTファイルとしてダウンロード",
        data=url_text.encode('utf-8'),
        file_name=txt_file_name,
        mime="text/plain",
    )

def display_final_dataframe(df_final, is_url=False):
    # 集計方法の説明
    st.markdown("#### 🧮段階の集計方法の説明")
    st.text("階層は、分類3ごとに集計しています。")
    st.text("分類3ごとに、各単語（分類4）の出現回数の合計値「M」を求め、下記で階層の値を算出しています。")
    code = """
            階層 = M ÷ 10 + 1
            （ただし、M = 0の場合、階層=0）
            """
    st.code(code, language='python')

    # 最終的なデータフレームを表示
    st.markdown("#### 📊集計表")
    if is_url:
        # URLリストがある場合のデータフレーム表示
        st.dataframe(df_final[['分類1', '分類2', '分類3', '分類4', '単語出現回数（合計）', '段階', '単語出現回数（個別）']].style.bar(subset=['単語出現回数（合計）'], color='#5fba7d'))
    else:
        # PDFファイルの場合のデータフレーム表示
        st.dataframe(df_final[['分類1', '分類2', '分類3', '分類4', '単語出現回数', '段階']].style.bar(subset=['単語出現回数'], color='#5fba7d'))

    # 処理完了メッセージ
    st.success('処理完了！')

if __name__ == "__main__":
    app()
