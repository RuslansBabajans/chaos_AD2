%% Clear variables
close all, clear variables;
format long;
%=============================%
n=1010; % number of bits 10000
m=round(32768/n); % number of samples per bit
t_delay=0; % delay bit stream
T=300e-6; % bit length
tau=T/m; % sampling step
Fs=round(1/tau);

time=t_delay:tau:T*n-tau+t_delay;

snr_levels=[20, 15, 10, 5, 0]; % 20, 15, 10, 5, 0


number=1:1:1; % !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

for o=1:length(snr_levels)

    
for num=1:1:length(number)  
Random_binary_sequence = randi([0, 1], 1,n);
%=============================%
X = Random_binary_sequence;
Y = ones(1,m);
K = kron(X,Y);

Information_signal=K;
writematrix(Random_binary_sequence,['RC1_original_bit_sequence_',num2str(snr_levels(o)),'_SNR_',num2str(number(num)),'.csv'])
writematrix(Information_signal,['RC1_info_signal_',num2str(snr_levels(o)),'_SNR_',num2str(number(num)),'.csv'])
% audiowrite(['RC1_info_dignal_',num2str(snr_levels),'_SNR_1.wav'],Information_signal,Fs)

end

end

% figure(1)
% plot(time,Information_signal)
% grid on, grid minor
