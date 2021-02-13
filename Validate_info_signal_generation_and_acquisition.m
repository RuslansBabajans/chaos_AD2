%% Clear variables and close figures
format long
clear variables
close all
%=============================%
%% Generated info signal parameters 
n=1010; % number of bits 10000
m=round(32768/n); % number of samples per bit
t_delay=0; % delay bit stream
T=300e-6; % bit length
tau=T/m; % sampling step
Fs=round(1/tau);

time_generated=t_delay:tau:T*n-tau+t_delay;

%=============================%
%% Generated info signal parameters

Fs_scope=1e6;
t_end=0.3;
time_vector=0:1/Fs_scope:t_end-1/Fs_scope;

snr_levels=[20 15 10 5 0]; % 20 15 10 5 0

for m=1:length(snr_levels)
Chaos_info_signal_master = readmatrix(['Chaos_info_signal_master_',num2str(snr_levels(m)),'_SNR_1.csv']);
Chaos_info_signal_slave = readmatrix(['Chaos_info_signal_slave_',num2str(snr_levels(m)),'_SNR_1.csv']);
Chaos_noise_signal_master = readmatrix(['Chaos_noise_signal_master_',num2str(snr_levels(m)),'_SNR_1.csv']);

Generated_info_signal = readmatrix(['RC1_info_signal_',num2str(snr_levels(m)),'_SNR_1.csv']);
Generated_info_signal=Generated_info_signal*5;

figure(m)
plot(time_vector,Chaos_info_signal_master)
hold on
plot(time_generated,Generated_info_signal)

% figure(2)
% plot(time_vector,Chaos_info_signal_slave)
% hold on
% plot(time_generated,Generated_info_signal)
% 
% figure(3)
% plot(time_vector,Chaos_noise_signal_master)
% hold on
% plot(time_generated,Generated_info_signal)

end


