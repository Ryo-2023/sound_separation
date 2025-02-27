import torch
import soundfile as sf
import matplotlib.pyplot as plt
import numpy as np
from tqdm import tqdm

import plot

torch.set_default_dtype(torch.float64)

class STFT():
    def __init__(self,source_path,n_fft=1024):
        self.path = source_path
        self.n_fft = n_fft
        self.F_bin = self.n_fft//2 + 1
        
        self.data_list, self.sr = self.get_reshaped_data()
        self.mixed_data = self.generate_mixed_data()
        
    def get_reshaped_data(self):
        data_list = []
        sr_list = []
        for path in self.path:
            data,sr = sf.read(path)
            data_list.append(data)
            sr_list.append(sr)
            
        # 長さを揃える
        min_len = min(len(data) for data in data_list)
        for i in range(len(data_list)):
            data_list[i] = data_list[i][:min_len]    
        
        data_list = torch.tensor(np.array(data_list))
        sr_list = torch.tensor(np.array(sr_list))
        
        # 正規化
        for i in range(len(data_list)):
            data_list[i] = data_list[i] / torch.max(torch.abs(data_list[i]))
            
        # 最小のサンプリング周波数
        min_sr = torch.min(sr_list)  
        
        return data_list, min_sr
        
    def generate_mixed_data(self):
        data_list = self.data_list
        
        # ノイズを加える
        data_list += torch.rand(data_list.shape)*2*1e-3 - 1e-3
        
        # 混合音の生成
        mixed_data = torch.sum(data_list,dim=0)
        mixed_data = mixed_data / torch.max(torch.abs(mixed_data))  # 正規化
        
        return mixed_data
        
    def stft(self,data):
        stft_result = torch.stft(data,n_fft=self.n_fft,hop_length=self.n_fft//4, window=torch.hann_window(self.n_fft), return_complex=True)
        
        # 振幅スペクトログラムと位相スペクトログラムに分ける
        amp = torch.abs(stft_result)
        phase = torch.angle(stft_result)
        
        return amp, phase
    
    def run_stft(self):
        data_amp = []
        data_phase = []
        for data in self.data_list:
            amp,phase = self.stft(data)
            data_amp.append(amp)
            data_phase.append(phase)
        data_amp = torch.stack(data_amp)
        data_phase = torch.stack(data_phase)
        
        mixed_amp, mixed_phase = self.stft(self.mixed_data)
        
        return data_amp, data_phase, mixed_amp, mixed_phase
    
def main():
    path = ["wav1.wav","wav2.wav"]
    stft = STFT(path)
    d_amp,d_phase,amp, phase = stft.run_stft()
    print("amp.shape:",amp.shape)
    print("phase.shape:",phase.shape)

    plot.plot_spectrogram(amp,stft.sr,"Mixed Spectrogram")
    
if __name__ == "__main__":
    main()