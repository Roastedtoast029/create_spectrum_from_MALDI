# 各種パラメータの管理
import numpy as np
import tkinter as tk

class Params:
    def __init__(self, master):
        # figsize = (12.7, 2.9)
        self.lower_limit = tk.DoubleVar(master, value=0.0)
        self.upper_limit = tk.DoubleVar(master, value=5000.0)
        self.use_filter = tk.BooleanVar(master, value=False)
        self.filter_sigma = tk.IntVar(master, value=15)
    
    def reflect_params(self, parent):
        # 各種パラメータ変更を反映
        self.change_limit(parent)

    # 表示範囲の変更
    def change_limit(self, parent):
        for ax in parent.axes:
            # x軸の変更
            ax.set_xlim(self.lower_limit.get(),self.upper_limit.get())
            # y軸の変更
            x,y = list(ax.lines[0].get_data())
            index_list = np.where((self.lower_limit.get()<=x) & (x<=self.upper_limit.get()))
            ax.set_ylim(0,y[index_list].max())