# app.py
import streamlit as st
from page import batch_process, batch_process_graph

# ページを追加するための辞書
PAGES = {    
    "単語出現回数カウント": batch_process,
    "グラフ描写": batch_process_graph
}

def main():
    st.sidebar.title("📜集計表サステナ単語カウントアプリ")
    
    selection = st.sidebar.selectbox("ページを選択", list(PAGES.keys()))
    page = PAGES[selection]
    
    # ここでpage.app()を呼び出す代わりに、選択されたページに応じた処理を行う
    page.app()

if __name__ == "__main__":
    main()
