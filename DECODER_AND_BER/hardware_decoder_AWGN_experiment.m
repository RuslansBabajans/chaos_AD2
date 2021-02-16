%% Clear variables and close figures
format long
clear variables
close all

%==============================================%
%% Scope and loop parameters 

Fs_scope=1e6;
t_end=0.3;
time=0:1/Fs_scope:t_end-1/Fs_scope;

snr_levels=[20 15 10 5 0];
number=1:1:1; % !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

% BER holders
ber_number=zeros(1,length(snr_levels));
ber_ratio=zeros(1,length(snr_levels));
%==============================================%
%% Calculate BEES for every experiment iterration

for num=1:1:length(number)
for m=1:length(snr_levels)


fprintf('Number = %d, snr_levels = %d dB\n', num, snr_levels(m))
fprintf('==============================================\n')

%==============================================%
%% Read saved scope signals

Chaos_info_signal_master = readmatrix(['Chaos_info_signal_master_',num2str(snr_levels(m)),'_SNR_',num2str(number(num)),'.csv']);
Chaos_info_signal_slave = readmatrix(['Chaos_info_signal_slave_',num2str(snr_levels(m)),'_SNR_',num2str(number(num)),'.csv']);
Chaos_noise_signal_master = readmatrix(['Chaos_noise_signal_master_',num2str(snr_levels(m)),'_SNR_',num2str(number(num)),'.csv']);

%==============================================%
%% Read original bit sequence

original_bit_sequence=readmatrix(['RC1_original_bit_sequence_',num2str(snr_levels(m)),'_SNR_',num2str(number(num)),'.csv']);

%==============================================%
%% Signals to calculate beta

V_master_signal=Chaos_info_signal_master+Chaos_noise_signal_master; % Received info signal from Master with noise
V_slave_signal=Chaos_info_signal_slave-mean(Chaos_info_signal_slave); % Slave local decode signal

%==============================================%
%% Create 100 us window

window=1; % start address
t_window=100e-6;
while time(window)<t_window
    window=window+1;
end

%==============================================%
%% Predefine vectors for correlation coefficient and time  

beta=zeros(1,length(time)-window);
T=zeros(1,length(time)-window);

%==============================================%
%% Calculte correlation coefficient using sliding window across all synchronizatio time interval

for o=1:1:(length(time)-window)   
 
x=V_master_signal(o:o+window);
y=V_slave_signal(o:o+window);

beta(o)=corr2(x,y);
T(o)=time(o+window);
end

%==============================================%
%% Decoder comparator

Threshold=0;

digital_comparator_out=zeros(1,length(beta));

for k=1:length(beta)
    if beta(k)>Threshold
      digital_comparator_out(k)=1;
    else
      digital_comparator_out(k)=0;  
    end
end

%==============================================%
%% Covert decoded signal to bit string

bit_length=300e-6;
number_of_received_bits=round(time(end)/bit_length);

% Predefine
adress_holder=zeros(1,(round(number_of_received_bits)+1));
time_holder=zeros(1,(round(number_of_received_bits)+1));
decoded_sequence=zeros(1,round(number_of_received_bits));

adress_holder(1)=1; % time vectors start
time_holder(1)=T(1); % time vectors start

for h=1:1:round(number_of_received_bits)
   
adress=find(abs(T-bit_length*h) < 0.00001); % find address of specific time point  % 0.000001
adress_holder(h+1)=adress(1);
time_holder(h+1)=T(adress(1));


decoded_sequence(h)=round(mean(digital_comparator_out(adress_holder(h):adress_holder(h+1))));

end

%==============================================%
%% BER calculation

ber_number(m)=0;

for bit_index=1:1:length(original_bit_sequence)
    if original_bit_sequence(bit_index)~= decoded_sequence(bit_index)
        ber_number(m)=ber_number(m)+1;
    end
end
ber_ratio(m)=ber_number(m)/length(original_bit_sequence);

%==============================================%
%% Save BER numbers

fileID = fopen(['BER_numbers_SNR_',num2str(number(num)),'.txt'],'wt');
fprintf(fileID,'%11s\r\n',...
'ber_numbers');
fprintf(fileID,'%11.8f\r\n',ber_number);

% fileID = fopen(['BER_numbers_SNR_',num2str(number(num)),'.txt'],'wt');
% fprintf(fileID,'%11s\r\n',...
% 'ber_numbers');
% fprintf(fileID,'%u\r\n',ber_number);

end
end