import matplotlib.pyplot as plt

def create_language_chart(data):
    labels = list(data.keys())
    values = list(data.values())

    plt.figure()
    plt.pie(values, labels=labels)
    file = "chart.png"
    plt.savefig(file)
    plt.close()
    return file