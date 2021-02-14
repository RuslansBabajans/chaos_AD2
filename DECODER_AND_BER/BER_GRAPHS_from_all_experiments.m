%% Clear variables and close figures
format long
clear variables
close all

%==============================================%
snr_levels=[20 15 10 5 0];

ber_results_10_5=zeros(1,length(snr_levels));
delimiterIn = '	'; % data separation 
headerlinesIn=1; % number of header lines from the top in the .txt file

for num=1:1:length(number)
saved_signals=importdata(['BER_numbers_SNR_',num2str(num),'.txt'],delimiterIn,headerlinesIn); % read data 
ber_10_3=saved_signals.data(:, 1)';
ber_results_10_5=ber_results_10_5+ber_10_3;
end

%% Plot data with SNR


figure(1)
semilogy(snr_levels,ber_rate,'ob-','LineWidth',2)
xlabel('SNR, dB')
ylabel('BER')
% ylim([1e-7, 1])
% set(gca, 'XLim', [-11, 21], 'XTick', -10:5:20,...
%     'XTickLabel', -10:5:20);
set(gca, 'FontName', 'Times New Roman')
grid on, grid minor
set(gca,'fontsize',15)
%=============================%
%% PLot data with Eb/N0
delta_f_noise=50e3-500e1;
delta_f_bit=1/300e-6;
x_offset=10*log10((delta_f_noise)/(delta_f_bit));
x_offset=round(x_offset,2);

figure(2)
semilogy(snr_levels+x_offset,ber_rate,'ob-','LineWidth',2)
xlabel('E_b/N_0, dB')
ylabel('BER')
% ylim([1e-7, 1])
% set(gca, 'XLim', [-11+x_offset, 21+x_offset], 'XTick', -10+x_offset:5:20+x_offset,...
%     'XTickLabel', -10+x_offset:5:20+x_offset);
set(gca, 'FontName', 'Times New Roman')
grid on, grid minor
set(gca,'fontsize',15)
%=============================%
%% Save Eb/N0 to text file

W=[snr_levels+x_offset; ber_rate];

fileID = fopen(['HARDWARE_AWGN_RC1_RESULTS.txt'],'wt');
fprintf(fileID,'%11s\t%11s\r\n',...
'ebita_n0','ber_rate');
fprintf(fileID,'%11.8f\t%11.8f\r\n',W);