import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
import openpyxl
from scipy.ndimage import gaussian_filter1d
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from Params import Params

class Spectrum_from_MALDI(tk.Frame):
    # コンストラクタ
    # tkにフレーム、ボタンを配置
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.title("MALDI用スペクトル表示ツール")
        self.master.geometry("1200x800+100+100")

        # 各種設定置き場
        self.sidebar_font=("Arial", "10")

        self.option_label_font=("Times", "18")
        self.option_entry_font=("Times", "18")
        self.option_entry_width=10

        # pyplotの初期設定
        plt.rcParams['font.family'] = 'Arial'
        # plt.rcParams['font.size'] = '20'

        # パラメータのインスタンスを生成
        self.params = Params(self.master)
       
        # フレームとボタンの作成
        self.sidebar_frame = self.create_sidebar_frame()
        self.graph_frame = self.create_graph_frame()

        # 配置
        self.sidebar_frame.pack(fill=tk.BOTH)
        self.graph_frame.pack(fill=tk.BOTH, expand=True)


    # matplotlib配置用フレームの作成
    def create_graph_frame(self):
        graph_frame = tk.Frame(self.master)
        
        # matplotlibの描画領域の作成
        self.fig = plt.figure()
        self.fig.subplots_adjust(
            top=0.95,
            bottom=0.1,
            left=0.1,
            right=0.9,
            hspace=0.5,
            wspace=0.2
        )
        # raw_dataの入れ子
        self.raw_datas = []
        # matplotlibの描画領域とウィジェット(Frame)の関連付け
        self.fig_canvas = FigureCanvasTkAgg(self.fig, graph_frame)
        # matplotlibのツールバーを作成
        self.toolbar = NavigationToolbar2Tk(self.fig_canvas, graph_frame)
        # matplotlibのグラフをフレームに配置
        self.fig_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        return graph_frame


    # サイドバー用フレーム
    def create_sidebar_frame(self):
        sidebar_frame = tk.Frame(self.master)

        file_button = tk.Button(
            sidebar_frame, 
            text = 'File', 
            font = self.sidebar_font,
            command = self.file_button_command
            )
        
        option_button = tk.Button(
            sidebar_frame, 
            text = "Option",
            font = self.sidebar_font,
            command = self.option_button_command
            )
        
        file_button.pack(side="left",ipadx=5,anchor=tk.W)
        option_button.pack(side="left",ipadx=5,anchor=tk.W)

        return sidebar_frame
    

    # 選択されたファイルからraw_dataを生成
    def get_raw_data_from_path(self):
        typ = [('テキストファイル', '*.txt')]
        # dir = "C:/"
        raw_data_path = tk.filedialog.askopenfilenames(
            filetypes = typ, 
            # initialdir = dir
        ) 
        
        # raw_dataを格納
        for i,path in enumerate(raw_data_path):
            f = open(path, "r")
            raw_data = list(map(lambda x: list(map(float, x.split())),f.readlines()))
            self.raw_datas.append(raw_data)


    # スペクトルの作成
    def create_spectrum(self):    
        # 既存のスペクトル削除
        plt.clf()

        # 複数のグラフを縦に並べる
        n_data = len(self.raw_datas)
        for i,raw_data in enumerate(self.raw_datas):

            # pd.DataFrameにしてm/zでグループ化
            df = pd.DataFrame(raw_data, columns=["m/z", "intensity"])
            # print(df.head())
            # print(df.groupby("m/z", as_index=False).sum())
            data = df.groupby("m/z", as_index=False).sum()

            # スペクトル追加
            ax = self.fig.add_subplot(n_data, 1, i+1)
            X = data[(self.params.lower_limit.get()<=data["m/z"]) & (data["m/z"]<=self.params.upper_limit.get())]["m/z"]
            y = data[(self.params.lower_limit.get()<=data["m/z"]) & (data["m/z"]<=self.params.upper_limit.get())]["intensity"]

            # スムージング
            if self.params.use_filter.get():
                y_smoothed = gaussian_filter1d(y, sigma=self.params.filter_sigma.get())
            else:
                y_smoothed = y

            ax.set_xlim(self.params.lower_limit.get(),self.params.upper_limit.get())
            ax.set_ylim(0,max(y_smoothed))
            if i == len(self.raw_datas)-1:
                ax.set_xlabel("m/z")
            ax.set_ylabel("Intensity")
            ax.ticklabel_format(style="sci", axis="y", scilimits=(0,0))

            ax.plot(X, y_smoothed, color="black", linewidth=2)

            # 右と上の枠線削除
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
        # グラフの描画
        self.fig_canvas.draw()
    
    
    # 「File」ボタンを押したときの処理
    def file_button_command(self):
        # raw_datas削除
        self.raw_datas = []

        # path取得
        self.get_raw_data_from_path()  

        # グラフ描画
        self.create_spectrum()

    # 「Option」ボタンを押したときの処理
    def option_button_command(self):
        # モーダル表示
        self.option_modal = tk.Toplevel(self)
        self.option_modal.title("オプション") # ウィンドウタイトル
        self.option_modal.geometry("600x400+200+200")

        # モーダルにする設定
        self.option_modal.grab_set()        # モーダルにする
        self.option_modal.focus_set()       # フォーカスを新しいウィンドウをへ移す
        self.option_modal.transient(self.master)   # タスクバーに表示しない

        # パラメータを入力できるダイアログ
        
        # （参考）
        # self.param_dialog = tk.StringVar()
        # option_entry = tk.Entry(
        #     self.option_modal,
        #     textvariable=self.param_dialog
        # )
        # option_entry.pack()

        # m/zの表示範囲
        mz_range_frame = tk.Frame(self.option_modal)
        mz_range_frame.pack(
            fill=tk.X,
            padx=30,
            pady=30
            )
        
        mz_range_label = tk.Label(
            mz_range_frame,
            text="m/z range",
            font=self.option_label_font
            )
        mz_range_label.pack(side="left",padx=15)

        lower_limit_entry = tk.Entry(
            mz_range_frame,
            textvariable=self.params.lower_limit,
            font=self.option_entry_font,
            width=self.option_entry_width
            )
        lower_limit_entry.pack(side="left",padx=15)
        
        upper_limit_entry = tk.Entry(
            mz_range_frame,
            textvariable=self.params.upper_limit,
            font=self.option_entry_font,
            width=self.option_entry_width
            )
        upper_limit_entry.pack(side="left",padx=15)

        use_filter_frame = tk.Frame(self.option_modal)
        use_filter_frame.pack(
            fill=tk.X,
            padx=30,
            pady=30
            )
        
        use_filter_label = tk.Label(
            use_filter_frame,
            text="gaussian filter",
            font=self.option_label_font
            )
        use_filter_label.pack(side="left",padx=15)

        use_filter_checkbox = tk.Checkbutton(use_filter_frame, variable=self.params.use_filter)
        use_filter_checkbox.pack(side="left",padx=15)  

        filter_sigma_frame = tk.Frame(self.option_modal)
        filter_sigma_frame.pack(
            fill=tk.X,
            padx=30,
            pady=30
            )
        
        filter_sigma_label = tk.Label(
            filter_sigma_frame,
            text="filter_sigma",
            font=self.option_label_font
            )
        filter_sigma_label.pack(side="left",padx=15)

        filter_sigma_entry = tk.Entry(
            filter_sigma_frame,
            textvariable=self.params.filter_sigma,
            font=self.option_entry_font,
            width=self.option_entry_width
            )
        filter_sigma_entry.pack(side="left",padx=15)    

        # 完了ボタンで閉じる＋パラメータ反映
        close_button = tk.Button(
            self.option_modal,
            text = '完了', 
            command = self.close_button_command
        )
        close_button.pack(
            side="bottom",
            anchor=tk.E,
            ipadx=20,
            ipady=3,
            padx=10,
            pady=10
        )
        

    # 「完了」ボタンを押したときの処理
    def close_button_command(self):
        # パラメータの変更を反映
        self.params.reflect_params(self)
        # モーダルの破棄
        self.option_modal.destroy()
        # グラフの再表示
        self.fig_canvas.draw()

root = tk.Tk()
app = Spectrum_from_MALDI(master=root)
app.mainloop()