%% Clear variables and close figures
format long
clear variables
close all
%=============================%
%% Read data acquired from AD2

Fs=1e6;
t_end=0.3;
time_vector=0:1/Fs:t_end-1/Fs;

snr_levels=[20 15 10 5 0]; % 20 15 10 5 0

for m=1:length(snr_levels)
Chaos_info_signal_master = readmatrix(['Chaos_info_signal_master_',num2str(snr_levels(m)),'_SNR.csv']);
Chaos_info_signal_slave = readmatrix(['Chaos_info_signal_slave_',num2str(snr_levels(m)),'_SNR.csv']);
Chaos_noise_signal_master = readmatrix(['Chaos_noise_signal_master_',num2str(snr_levels(m)),'_SNR.csv']);

% figure(1)
% plot(time_vector,Chaos_info_signal_master)
% hold on
% 
% figure(2)
% plot(time_vector,Chaos_info_signal_slave)
% hold on
% 
% figure(3)
% plot(time_vector,Chaos_noise_signal_master)
% hold on

if snr_levels(m)==0
    figure(4)
    plot(time_vector,Chaos_info_signal_slave)
    hold on
    plot(time_vector,Chaos_info_signal_slave)
    plot(time_vector,Chaos_noise_signal_master)
end


if snr_levels(m)==5
    figure(5)
    plot(time_vector,Chaos_info_signal_slave)
    hold on
    plot(time_vector,Chaos_info_signal_slave)
    plot(time_vector,Chaos_noise_signal_master)
end
if snr_levels(m)==10
    figure(6)
    plot(time_vector,Chaos_info_signal_slave)
    hold on
    plot(time_vector,Chaos_info_signal_slave)
    plot(time_vector,Chaos_noise_signal_master)
end

if snr_levels(m)==15
    figure(7)
    plot(time_vector,Chaos_info_signal_slave)
    hold on
    plot(time_vector,Chaos_info_signal_slave)
    plot(time_vector,Chaos_noise_signal_master)
end

if snr_levels(m)==20
    figure(8)
    plot(time_vector,Chaos_info_signal_slave)
    hold on
    plot(time_vector,Chaos_info_signal_slave)
    plot(time_vector,Chaos_noise_signal_master)
end

end
%% Format figure
% figure(1)
% xlabel('t, s')
% grid on, grid minor
% % set(gca, 'XLim', [100, 300], 'XTick', 100:10:300,...
% %     'XTickLabel', 100:10:300);
% % set(gca, 'YLim', [0, 1], 'YTick', 0:0.05:1,...
% %     'YTickLabel', 0:0.05:1);
% set(gca, 'FontName', 'Times New Roman')
% % set(gca,'fontsize',24)
% legend([ num2str(snr_levels(1)) ' dB'],[ num2str(snr_levels(2)) ' dB'],[ num2str(snr_levels(3)) ' dB'],[ num2str(snr_levels(4)) ' dB'],[ num2str(snr_levels(5)) ' dB'],'Location','best');
