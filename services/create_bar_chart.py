import plotly.express as px

def create_bar_chart(df):
    # 棒グラフの作成
    fig = px.bar(df, y='分類4', x='単語出現回数', orientation='h', 
                title="単語出現回数の棒グラフ",
                template="plotly_white",  # 明るいテーマで背景を白に
                )

    # 外枠の表示設定
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',  # グラフの背景色を透明に
        xaxis=dict(showgrid=True, gridcolor='lightgrey'),  # X軸のメッシュ線を表示
        yaxis=dict(showgrid=True, gridcolor='lightgrey'),  # Y軸のメッシュ線を表示
        margin=dict(l=20, r=20, t=30, b=20),  # グラフのマージン設定
    )

    # グラフの軸ラベルの設定
    fig.update_xaxes(title_text='単語出現回数')
    fig.update_yaxes(title_text='分類')

    return fig