%% Clear variables and close figures
format long
clear variables
close all
%=============================%
%% Read data acquired from AD2
color_code=["#77AC30","#4DBEEE","#A2142F","#0072BD","#D95319"];
Fs=2e6;
t_end=0.05;
time_vector=0:1/Fs:t_end-1/Fs;

snr_levels=[20 15 10 5 0]; % 20 15 10 5 0

for m=1:length(snr_levels)
Chaos_info_signal_master = readmatrix(['C:\Users\xuxla\PycharmProjects\pythonProject1\Chaos_info_signal_master_',num2str(snr_levels(m)),'_SNR.csv']);
Chaos_info_signal_slave = readmatrix(['C:\Users\xuxla\PycharmProjects\pythonProject1\Chaos_info_signal_slave_',num2str(snr_levels(m)),'_SNR.csv']);
Chaos_noise_signal_master = readmatrix(['C:\Users\xuxla\PycharmProjects\pythonProject1\Chaos_noise_signal_master_',num2str(snr_levels(m)),'_SNR.csv']);

%%
iterration=m % Show iterration step

V_master_signal=Chaos_info_signal_master+Chaos_noise_signal_master; % Masters chaotic signal
V_slave_signal=Chaos_info_signal_slave; % Slaves chaotic signal

%figure(2),plot(time_vector,V_master_signal,time_vector,V_slave_signal)

window=1; % start address
t_window=100e-6;
while time_vector(window)<t_window
    window=window+1;
end

% Calculte correlation coefficient using sliding window across all synchronizatio time interval
beta=zeros(1,length(time_vector)-window);
T=zeros(1,length(time_vector)-window);

for o=1:1:(length(time_vector)-window)   
 
x=V_master_signal(o:o+window);
y=V_slave_signal(o:o+window);

beta(o)=corr2(x,y);
T(o)=time_vector(o+window);
end

figure(1)
plot(T*1e6,beta,'LineWidth',2,'color',color_code(m))
hold on
end
%% Format figure
figure(1)
xlabel('t, \mus')
ylabel('\beta(t)')
grid on, grid minor
set(gca, 'XLim', [100, 300], 'XTick', 100:10:300,...
    'XTickLabel', 100:10:300);
set(gca, 'YLim', [0, 1], 'YTick', 0:0.05:1,...
    'YTickLabel', 0:0.05:1);
set(gca, 'FontName', 'Times New Roman')
set(gca,'fontsize',24)
legend([ num2str(snr_levels(1)) ' dB'],[ num2str(snr_levels(2)) ' dB'],[ num2str(snr_levels(3)) ' dB'],[ num2str(snr_levels(4)) ' dB'],[ num2str(snr_levels(5)) ' dB'],'Location','best');
