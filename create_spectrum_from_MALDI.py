import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
import openpyxl
from scipy.ndimage import gaussian_filter1d
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

class Spectrum_from_MALDI(tk.Frame):
    # コンストラクタ
    # tkにフレーム、ボタンを配置
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.title("MALDI用スペクトル表示ツール")

        # pyplotの初期設定
        plt.rcParams['font.family'] = 'Arial'
        plt.rcParams['font.size'] = '20'
        plt.subplots_adjust(
            top=0.92,
            bottom=0.22,
            left=0.125,
            right=0.9,
            hspace=0.2,
            wspace=0.2
        )
       
        # フレームとボタンの作成
        self.graph_frame = self.create_graph_frame()
        self.file_frame = self.create_file_frame()
        self.option_button = tk.Button(
                                self.master, 
                                text = "オプション", 
                                #   command = self.get_params
                                )

        # 配置
        self.graph_frame.pack(fill=tk.BOTH, expand=True)
        self.file_frame.pack()
        self.option_button.pack()


    # matplotlib配置用フレームの作成
    def create_graph_frame(self):
        graph_frame = tk.Frame(self.master)
        
        # matplotlibの描画領域の作成
        self.fig = plt.figure()
        # matplotlibの描画領域とウィジェット(Frame)の関連付け
        self.fig_canvas = FigureCanvasTkAgg(self.fig, graph_frame)
        # matplotlibのツールバーを作成
        self.toolbar = NavigationToolbar2Tk(self.fig_canvas, graph_frame)
        # matplotlibのグラフをフレームに配置
        self.fig_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        return graph_frame
    

    # ファイル選択フレーム
    def create_file_frame(self):
        file_frame = tk.Frame(self.master)

        # ラベル
        tk.Label(file_frame, text = "ファイル").pack(side = tk.LEFT)
        # テキストボックスの作成と配置
        file_frame.edit_box = tk.Entry(file_frame, width = 50)
        file_frame.edit_box.pack(side = tk.LEFT, expand=True)
        # ボタンの作成と配置
        file_button = tk.Button(
            file_frame, 
            text = 'ファイルを選択', 
            command = self.file_button_command
        )
        file_button.pack(side = tk.LEFT)

        return file_frame
    

    # 元データのファイルパスを返す
    def get_raw_data_path(self):
        typ = [('テキストファイル', '*.txt')]
        dir = "C:/"
        raw_data_path = tk.filedialog.askopenfilenames(
            filetypes = typ, 
            initialdir = dir
        ) 
        return raw_data_path
    

    # スペクトルの作成
    def create_spectrum(self, raw_data_path):        
        # 複数のグラフを縦に並べる
        n_data = len(raw_data_path)
        for i,path in enumerate(raw_data_path):
            f = open(path, "r")
            raw_data = list(map(lambda x: list(map(float, x.split())),f.readlines()))

            # pd.DataFrameにしてm/zでグループ化
            df = pd.DataFrame(raw_data, columns=["m/z", "intensity"])
            # print(df.head())
            # print(df.groupby("m/z", as_index=False).sum())
            data = df.groupby("m/z", as_index=False).sum()

            # スペクトル追加
            ax = self.fig.add_subplot(n_data, 1, i+1)
            X = data[(self.params.lower_limit<=data["m/z"]) & (data["m/z"]<=self.params.upper_limit)]["m/z"]
            y = data[(self.params.lower_limit<=data["m/z"]) & (data["m/z"]<=self.params.upper_limit)]["intensity"]

            # スムージング
            y_smoothed = gaussian_filter1d(y, sigma=7)

            ax.set_xlim(self.params.lower_limit,self.params.upper_limit)
            ax.set_ylim(0,max(y_smoothed))
            ax.set_xlabel("m/z")
            ax.set_ylabel("Intensity")

            ax.plot(X, y_smoothed, color="black", linewidth=2)

            # 右と上の枠線削除
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)

        # グラフの描画
        self.fig_canvas.draw()
    
    
    #「ファイルを選択」ボタンを押したときの処理
    def file_button_command(self):
        # path取得
        raw_data_path = self.get_raw_data_path()    

        # 既存のグラフ削除    
        plt.clf()

        # テキストボックスの更新
        self.file_frame.edit_box.delete(0, tk.END)
        self.file_frame.edit_box.insert(tk.END, ",".join(raw_data_path))

        # グラフ描画
        self.create_spectrum(raw_data_path)

    
    # 各種パラメータの初期設定、変更する場合はget_paramsを使用する
    class Params:
        figsize = (12.7, 2.9)
        lower_limit = 0
        upper_limit = 5000
    params = Params()

    # def get_params(self, ):
    #     return

root = tk.Tk()
app = Spectrum_from_MALDI(master=root)
app.mainloop()