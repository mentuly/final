import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

def plot_pie_chart(data):
    # кільцева діаграма
    labels = data.keys()
    sizes = data.values()

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # для того, щоб діаграма була круглою
    plt.show()

def plot_bar_chart(data):
    # стовпчикова діаграма
    labels = data.keys()
    sizes = data.values()

    fig, ax = plt.subplots()
    ax.bar(labels, sizes)
    ax.set_xlabel('Категорії')
    ax.set_ylabel('Використано (ГБ)')
    plt.show()

def plot_line_chart(data):
    # лінійна діаграма
    labels = list(data.keys())
    sizes = list(data.values())

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=labels, y=sizes, mode='lines+markers', name='Використання диску'))
    fig.update_layout(title="Використання диску з часом", xaxis_title="Категорії", yaxis_title="Використано (ГБ)")
    fig.show()

def plot_usage(data, chart_type='pie'):
    # діаграми залежно від типу
    if chart_type == "pie":
        plot_pie_chart(data)
    elif chart_type == "bar":
        plot_bar_chart(data)
    elif chart_type == "online_pie":
        fig = px.pie(names=list(data.keys()), values=list(data.values()), title="Використання диску (Інтерактивне)")
        fig.show()
    elif chart_type == "online_bar":
        fig = px.bar(x=list(data.keys()), y=list(data.values()), title="Використання диску (Інтерактивне)")
        fig.show()
    elif chart_type == "online_line":
        plot_line_chart(data)
    else:
        raise ValueError(f"Не підтримуваний тип діаграми: {chart_type}")