function MESH_SUMMA_SF()

% The purpose this function is to read MESH and SUMMA Streamflow estimates
% to see how two model are compareble. The new_rank is used to reorder
% SUMMA runoff estimates. 
%
%
% Input 
%
%
% Output 
%
% Reference 
%
% See also 
%
% Auhtor : Ala Bahrami 
%
%
% Created : 03/27/2021
%
% Last Modified : 
%
%% Copyright (C) 2021 Ala Bahrami  
    if nargin == 0
        prmname          = 'MESH_SUMMA.txt';
    end 
    fid  = fopen(prmname);
    Info = textscan(fid, '%s %s');
    fclose(fid);
%% Time index
    ts = datetime(2000,10,01,00,00,00);
    tf = datetime(2013,09,30,00,00,00);
    time = ts : hours(1): tf;
    time_y = ts : calyears(2): tf;
    time_d = ts : caldays(1): tf;
    
    % finding subset of data
    rs   = find(time == '08-June-2003 00:00:00');
    rf   = find(time == '04-July-2003 00:00:00');
    
%     rs   = find(time == '28-May-2001 00:00:00');
%     rf   = find(time == '03-June-2001 23:00:00');
    
    rs_d = find(time_d == '08-June-2003 00:00:00');
    rf_d = find(time_d == '04-July-2003 00:00:00');
    
%     rs_d = find(time_d == '28-May-2001 00:00:00');
%     rf_d = find(time_d == '03-June-2001 00:00:00');
     
%% reading Rank and MESH outputs  
    new_rank = dlmread(Info{1,2}{2,1}) + 1;
    STFL     = xlsread(Info{1,2}{1,1}); 
    STFL(:,1)= [];
    STFL_QI  = xlsread(Info{1,2}{5,1});
    STFL_QI(:,1) = [];
    STFL_RFF  = xlsread(Info{1,2}{6,1});
    STFL_RFF(:,1) = [];
    
%% Reading basin area with 
    BA = ncread(Info{1,2}{4,1}, 'basin_area');
    BA = BA(new_rank);
    
%% Reading SUMMA files 
    Infonc            = ncinfo(Info{1,2}{3,1});
    Infonc2           = ncinfo(Info{1,2}{7,1});
    Infonc3           = ncinfo(Info{1,2}{8,1});
    
    rk                = Infonc.Variables(5).Size(1);
    tt                = Infonc.Variables(5).Size(2);
    STFL_SM           = zeros (tt, rk, 4);
    DataName          = cell(5,1);
    
    for i = 0 : 4
        STFL_SM(:,:,i+1) = ncread(Info{1,2}{3,1}, Infonc.Variables(4+i).Name)';
        STFL_SM(:,:,i+1) = STFL_SM(:,new_rank,i+1);
        if (i == 0)
            STFL_SM(:,:,i+1) = STFL_SM(:,:,i+1) * 3600 * 1000;
        end 
        DataName{i+1,:}  = Infonc.Variables(4+i).Name;
    end

    RFF_SM =  ncread(Info{1,2}{7,1}, Infonc2.Variables(4).Name);
    sigid  =  ncread(Info{1,2}{8,1}, Infonc3.Variables(7).Name);
    
%% plot style 
    color ={[0.35 0.35 0.35],[0.850 0.325 0.0980],[0.055 0.310 0.620],...
                                 [0 0.48 0.070],'m','w'};
    lsty  =  {'-','--','-.'};

%% assign title 
    tl = cell(rk , 1);
    for i = 1 : rk 
           str    = sprintf('segid-%d',sigid(i));
           tl{i}  = strcat('BowBanff ', '-' , str); 
    end 
    
%% Calculate PBIAS 
% ! check if the calculation is correct 
%     PBIAS = zeros(rk, 1);
%     
%     for i = 1 : rk
%         RFF_mean      = mean(STFL_SM(: , i, 1));
%         errd(:,1)     = STFL_RFF(: , i) - STFL_SM(: , i, 1);
%         bias(1,1)     = sum(errd(:,1)) ./ (RFF_mean * tt);
%         PBIAS(i)      = bias(1,1) * 100;
%     end 

%% display MESH QI, QO, RFF for three upstream location (RANK1, RANK2, RANK6)
    % convert RFF to rate 
    RFF6 = STFL_RFF(rs:rf , 6)* BA(6)/(3600*1000);
    
    outdir = 'output\BowBanff\QI_QO_RFF\';
    
    lg = {'QO_{71032409}','QO_{71032292}','QI_{71030270}','RFF_{71030270}', '[QO_{71032409} + QO_{71032292} + RFF_{71030270}]'};
    
    fig = figure ('units','normalized','outerposition',[0 0 1 1]);
    subplot(2,1,1)
    % QO
    h = plot(time(rs:rf), STFL(rs:rf , 1));
    h.LineStyle =  lsty{1};
    h.LineWidth = 2;
    h.Color = color{1};
    hold on 
    %QO
    h = plot(time(rs:rf), STFL(rs:rf , 2));
    h.LineStyle =  lsty{2};
    h.LineWidth = 2;
    h.Color = color{2};
    % QI
    h = plot(time(rs:rf), STFL_QI(rs:rf , 6));
    h.LineStyle =  lsty{3};
    h.LineWidth = 2;
    h.Color = color{3};
    % RFF
    h = plot(time(rs:rf), RFF6);
    h.LineStyle =  lsty{1};
    h.LineWidth = 2;
    h.Color = color{5};
    % QO + RFF
    h = plot(time(rs:rf), STFL(rs:rf , 1) + STFL(rs:rf , 2) + RFF6 ,'DatetimeTickFormat' , 'yyyy-MMM-dd');
    h.LineStyle =  lsty{1};
    h.LineWidth = 2;
    h.Color = color{4};

    grid on 
    % Axis Labels
    xlabel('\bf Time [hours]','FontSize',14,'FontName', 'Times New Roman');
    ylabel('\bf Flow rate [m^{3}/s]','FontSize',14,'FontName', 'Times New Roman');
    title('MESH flows','FontSize',14,...
             'FontWeight','bold','FontName', 'Times New Roman')

    % Axis limit
    % xlimit
    xlim([time(rs) time(rf)])

    % Axis setting
    ax = gca; 
    set(ax , 'FontSize', 14,'FontWeight','bold','FontName', 'Times New Roman')
    ax.GridAlpha = 0.4;
    ax.GridColor = [0.65, 0.65, 0.65];
    ax.XTick = time_d;

    h = legend(lg{:});
    h.Location = 'northeast'; 
    h.FontSize = 14;
    h.Orientation = 'horizontal';
    h.EdgeColor = color{end};
    
    % plot the difference QI - (QO)  

    lg = {'QI_{71030270} - [QO_{71032409} + QO_{71032292} + RFF_{71030270}]'};
    subplot(2,1,2)
    h = plot(time(rs:rf), STFL_QI(rs:rf , 6) - STFL(rs:rf , 1) - STFL(rs:rf , 2)  - RFF6,'DatetimeTickFormat' , 'yyyy-MMM-dd');
    h.LineStyle =  lsty{1};
    h.LineWidth = 2;
    h.Color = color{1};
    
    % Axis Labels
    xlabel('\bf Time [hours]','FontSize',14,'FontName', 'Times New Roman');
    ylabel('\bf Flow rate [m^{3}/s]','FontSize',14,'FontName', 'Times New Roman');
    title('MESH flows','FontSize',14,...
             'FontWeight','bold','FontName', 'Times New Roman')

    % Axis limit
    % xlimit
    xlim([time(rs) time(rf)])

    % Axis setting
    ax = gca; 
    set(ax , 'FontSize', 14,'FontWeight','bold','FontName', 'Times New Roman')
    ax.GridAlpha = 0.4;
    ax.GridColor = [0.65, 0.65, 0.65];
    ax.XTick = time_d;

    h = legend(lg{:});
    h.Location = 'northwest'; 
    h.FontSize = 14;
    h.Orientation = 'horizontal';
    h.EdgeColor = color{end};
    
    fs1 = strcat(outdir, 'MESH-QIORFF' ,'.fig');
    fs2 = strcat(outdir, 'MESH-QIORFF','.png');
    %saveas(fig, fs1);
    %saveas(fig, fs2);
    %close(fig);

%% display  MizuRoute QI, QO(kwt), RFF for three upstream location (RANK1, RANK2, RANK6)   
    RFF6_SM = STFL_SM(rs:rf , 6 , 1)* BA(6)/(3600*1000);

    fig = figure ('units','normalized','outerposition',[0 0 1 1]);
    lg = {'KWTRFF_{71032409}','KWTRFF_{71032292}','sumUpRFF_{71030270}','basRFF_{71030270}',...
         '[KWTRFF_{71032409} + KWTRFF_{71032292} + basRFF_{71030270}]'};
    subplot(2,1,1)
    % QO
    h = plot(time(rs:rf), STFL_SM(rs:rf , 1, 4));
    h.LineStyle =  lsty{1};
    h.LineWidth = 2;
    h.Color = color{1};
    hold on 
    %QO
    h = plot(time(rs:rf), STFL_SM(rs:rf , 2, 4));
    h.LineStyle =  lsty{2};
    h.LineWidth = 2;
    h.Color = color{2};
    % QI
    h = plot(time(rs:rf), STFL_SM(rs:rf , 6, 3));
    h.LineStyle =  lsty{3};
    h.LineWidth = 2;
    h.Color = color{3};
    % RFF
    h = plot(time(rs:rf), RFF6_SM);
    h.LineStyle =  lsty{1};
    h.LineWidth = 2;
    h.Color = color{5};
    % QO + RFF
    h = plot(time(rs:rf), STFL_SM(rs:rf , 1, 4) + STFL_SM(rs:rf , 2, 4) +...
        RFF6_SM ,'DatetimeTickFormat' , 'yyyy-MMM-dd');
    h.LineStyle =  lsty{1};
    h.LineWidth = 2;
    h.Color = color{4};

    grid on 
    % Axis Labels
    xlabel('\bf Time [hours]','FontSize',14,'FontName', 'Times New Roman');
    ylabel('\bf Flow rate [m^{3}/s]','FontSize',14,'FontName', 'Times New Roman');
    title('MizuRoute flows','FontSize',14,...
             'FontWeight','bold','FontName', 'Times New Roman')

    % Axis limit
    % xlimit
    xlim([time(rs) time(rf)])

    % Axis setting
    ax = gca; 
    set(ax , 'FontSize', 14,'FontWeight','bold','FontName', 'Times New Roman')
    ax.GridAlpha = 0.4;
    ax.GridColor = [0.65, 0.65, 0.65];
    ax.XTick = time_d;
    
    h = legend(lg{:});
    h.Location = 'northeast'; 
    h.FontSize = 14;
    h.Orientation = 'horizontal';
    h.EdgeColor = color{end};
    
    % plot the difference QI - (QO)  
    lg = {'sumUpRFF_{71030270} - [KWTRFF_{71032409} + KWTRFF_{71032292} + basRFF_{71030270}]'};
    subplot(2,1,2)
    h = plot(time(rs:rf), STFL_SM(rs:rf , 6, 3) - STFL_SM(rs:rf , 1, 4) - ...
        STFL_SM(rs:rf , 2, 4)  - RFF6_SM,'DatetimeTickFormat' , 'yyyy-MMM-dd');
    h.LineStyle =  lsty{1};
    h.LineWidth = 2;
    h.Color = color{1};
    
    % Axis Labels
    xlabel('\bf Time [hours]','FontSize',14,'FontName', 'Times New Roman');
    ylabel('\bf Flow rate [m^{3}/s]','FontSize',14,'FontName', 'Times New Roman');
    title('MizuRoute flows','FontSize',14,...
             'FontWeight','bold','FontName', 'Times New Roman')

    % Axis limit
    % xlimit
    xlim([time(rs) time(rf)])

    % Axis setting
    ax = gca; 
    set(ax , 'FontSize', 14,'FontWeight','bold','FontName', 'Times New Roman')
    ax.GridAlpha = 0.4;
    ax.GridColor = [0.65, 0.65, 0.65];
    ax.XTick = time_d;

    h = legend(lg{:});
    h.Location = 'northwest'; 
    h.FontSize = 14;
    h.Orientation = 'horizontal';
    h.EdgeColor = color{end};

    fs1 = strcat(outdir, 'MizuRoute-QIORFF' ,'.fig');
    fs2 = strcat(outdir, 'MizuRoute-QIORFF','.png');
    %saveas(fig, fs1);
    %saveas(fig, fs2);
    %close(fig);

%% Display MESH vs MizuRoute QI, QO, RFF for Rank 1,2,6

    lg = {'QI_{71032409}','sumUpRFF_{71032409}','QI_{71032292}','sumUpRFF_{71032292}',...
        'QI_{71030270}','sumUpRFF_{71030270}'};

    fig = figure ('units','normalized','outerposition',[0 0 1 1]);
    %subplot(3,1,1)
    
    % QI MESH & Miz RANK1
    h = plot(time(rs:rf), STFL_QI(rs:rf , 1));
    h.LineStyle =  lsty{1};
    h.LineWidth = 2;
    h.Color = color{4};
    hold on
    h = plot(time(rs:rf), STFL_SM(rs:rf , 1, 3));
    h.LineStyle =  lsty{2};
    h.LineWidth = 2;
    h.Color = color{4};
    
    % QI MESH & Miz RANK2
    h = plot(time(rs:rf), STFL_QI(rs:rf , 2));
    h.LineStyle =  lsty{1};
    h.LineWidth = 2;
    h.Color = color{2};
    hold on
    h = plot(time(rs:rf), STFL_SM(rs:rf , 2, 3));
    h.LineStyle =  lsty{2};
    h.LineWidth = 2;
    h.Color = color{2};
    
    % QI MESH & Miz RANK6
    h = plot(time(rs:rf), STFL_QI(rs:rf , 6));
    h.LineStyle =  lsty{1};
    h.LineWidth = 2;
    h.Color = color{3};
    hold on
    h = plot(time(rs:rf), STFL_SM(rs:rf , 6, 3),'DatetimeTickFormat' , 'yyyy-MMM-dd');
    h.LineStyle =  lsty{2};
    h.LineWidth = 2;
    h.Color = color{3};
    
    % Axis Labels
    xlabel('\bf Time [hours]','FontSize',14,'FontName', 'Times New Roman');
    ylabel('\bf Flow rate [m^{3}/s]','FontSize',14,'FontName', 'Times New Roman');
    title('Inflow','FontSize',14,...
             'FontWeight','bold','FontName', 'Times New Roman')

    % Axis limit
    % xlimit
    xlim([time(rs) time(rf)])

    % Axis setting
    ax = gca; 
    set(ax , 'FontSize', 14,'FontWeight','bold','FontName', 'Times New Roman')
    ax.GridAlpha = 0.4;
    ax.GridColor = [0.65, 0.65, 0.65];
    ax.XTick = time_d;

    h = legend(lg{:});
    h.Location = 'northwest'; 
    h.FontSize = 14;
    h.Orientation = 'horizontal';
    h.EdgeColor = color{end};
    
    fs1 = strcat(outdir, 'MESH-MizuRoute-QI' ,'.fig');
    fs2 = strcat(outdir, 'MESH-MizuRoute-QI','.png');
    %saveas(fig, fs1);
    %saveas(fig, fs2);
    %close(fig);
    
    lg = {'QO_{71032409}','KWTRFF_{71032409}','QO_{71032292}','KWTRFF_{71032292}',...
        'QO_{71030270}','KWTRFF_{71030270}'};

    %subplot(3,1,2)
    % QO MESH & Miz RANK1 
    fig = figure ('units','normalized','outerposition',[0 0 1 1]);
    h = plot(time(rs:rf), STFL(rs:rf , 1));
    h.LineStyle =  lsty{1};
    h.LineWidth = 2;
    h.Color = color{4};
    hold on
    h = plot(time(rs:rf), STFL_SM(rs:rf , 1, 4));
    h.LineStyle =  lsty{2};
    h.LineWidth = 2;
    h.Color = color{4};
    
    % QO MESH & Miz RANK2 
    h = plot(time(rs:rf), STFL(rs:rf , 2));
    h.LineStyle =  lsty{1};
    h.LineWidth = 2;
    h.Color = color{2};
    hold on
    h = plot(time(rs:rf), STFL_SM(rs:rf , 2, 4));
    h.LineStyle =  lsty{2};
    h.LineWidth = 2;
    h.Color = color{2};
    
    % QO MESH & Miz RANK6 
    h = plot(time(rs:rf), STFL(rs:rf , 6));
    h.LineStyle =  lsty{1};
    h.LineWidth = 2;
    h.Color = color{3};
    hold on
    h = plot(time(rs:rf), STFL_SM(rs:rf , 6, 4),'DatetimeTickFormat' , 'yyyy-MMM-dd');
    h.LineStyle =  lsty{2};
    h.LineWidth = 2;
    h.Color = color{3};
    
    % Axis Labels
    xlabel('\bf Time [hours]','FontSize',14,'FontName', 'Times New Roman');
    ylabel('\bf Flow rate [m^{3}/s]','FontSize',14,'FontName', 'Times New Roman');
    title('Outflow','FontSize',14,...
             'FontWeight','bold','FontName', 'Times New Roman')

    % Axis limit
    % xlimit
    xlim([time(rs) time(rf)])

    % Axis setting
    ax = gca; 
    set(ax , 'FontSize', 14,'FontWeight','bold','FontName', 'Times New Roman')
    ax.GridAlpha = 0.4;
    ax.GridColor = [0.65, 0.65, 0.65];
    ax.XTick = time_d;

    h = legend(lg{:});
    h.Location = 'northwest'; 
    h.FontSize = 14;
    h.Orientation = 'horizontal';
    h.EdgeColor = color{end};
    
    fs1 = strcat(outdir, 'MESH-MizuRoute-QO' ,'.fig');
    fs2 = strcat(outdir, 'MESH-MizuRoute-QO','.png');
    %saveas(fig, fs1);
    %saveas(fig, fs2);
    %close(fig);
    
    lg = {'RFF_{71032409}','basRFF_{71032409}','RFF_{71032292}','basRFF_{71032292}',...
        'RFF_{71030270}','basRFF_{71030270}'};
    %subplot(3,1,3)
    
    % RFF MESH & Miz RANK1 
    fig = figure ('units','normalized','outerposition',[0 0 1 1]);
    h = plot(time(rs:rf), STFL_RFF(rs:rf , 1)*BA(1)/(3600*1000));
    h.LineStyle =  lsty{1};
    h.LineWidth = 2;
    h.Color = color{4};
    hold on
    h = plot(time(rs:rf), STFL_SM(rs:rf , 1, 1)*BA(1)/(3600*1000));
    h.LineStyle =  lsty{2};
    h.LineWidth = 2;
    h.Color = color{4};
    
    % RFF MESH & Miz RANK2 
    h = plot(time(rs:rf), STFL_RFF(rs:rf , 2)*BA(2)/(3600*1000));
    h.LineStyle =  lsty{1};
    h.LineWidth = 2;
    h.Color = color{2};
    hold on
    h = plot(time(rs:rf), STFL_SM(rs:rf , 2, 1)*BA(2)/(3600*1000));
    h.LineStyle =  lsty{2};
    h.LineWidth = 2;
    h.Color = color{2};

    % RFF MESH & Miz RANK6 
    h = plot(time(rs:rf), STFL_RFF(rs:rf , 6)*BA(6)/(3600*1000));
    h.LineStyle =  lsty{1};
    h.LineWidth = 2;
    h.Color = color{3};
    hold on
    h = plot(time(rs:rf), STFL_SM(rs:rf , 6, 1)*BA(6)/(3600*1000),'DatetimeTickFormat' , 'yyyy-MMM-dd');
    h.LineStyle =  lsty{2};
    h.LineWidth = 2;
    h.Color = color{3};

    % Axis Labels
    xlabel('\bf Time [hours]','FontSize',14,'FontName', 'Times New Roman');
    ylabel('\bf Flow rate [m^{3}/s]','FontSize',14,'FontName', 'Times New Roman');
    title('Runoff','FontSize',14,...
             'FontWeight','bold','FontName', 'Times New Roman')

    % Axis limit
    % xlimit
    xlim([time(rs) time(rf)])

    % Axis setting
    ax = gca; 
    set(ax , 'FontSize', 14,'FontWeight','bold','FontName', 'Times New Roman')
    ax.GridAlpha = 0.4;
    ax.GridColor = [0.65, 0.65, 0.65];
    ax.XTick = time_d;

    h = legend(lg{:});
    h.Location = 'northwest'; 
    h.FontSize = 14;
    h.Orientation = 'horizontal';
    h.EdgeColor = color{end};
    
    fs1 = strcat(outdir, 'MESH-MizuRoute-RFF' ,'.fig');
    fs2 = strcat(outdir, 'MESH-MizuRoute-RFF','.png');
    %saveas(fig, fs1);
    %saveas(fig, fs2);
    %close(fig);

%% Display MESH vs MizuRoute QI, QO, RFF for Rank 51
    
    lg = {'QI_{71028585}','sumUpRFF_{71028585}'};

    fig = figure ('units','normalized','outerposition',[0 0 1 1]);
    %subplot(3,1,1)
    
    % QI MESH & Miz RANK51
    h = plot(time(rs:rf), STFL_QI(rs:rf , 51));
    h.LineStyle =  lsty{1};
    h.LineWidth = 2;
    h.Color = color{4};
    hold on
    h = plot(time(rs:rf), STFL_SM(rs:rf , 51, 3),'DatetimeTickFormat' , 'yyyy-MMM-dd');
    h.LineStyle =  lsty{2};
    h.LineWidth = 2;
    h.Color = color{4};
    
    % Axis Labels
    xlabel('\bf Time [hours]','FontSize',14,'FontName', 'Times New Roman');
    ylabel('\bf Flow rate [m^{3}/s]','FontSize',14,'FontName', 'Times New Roman');
    title('Inflow','FontSize',14,...
             'FontWeight','bold','FontName', 'Times New Roman')

    % Axis limit
    % xlimit
    xlim([time(rs) time(rf)])
    % Axis setting
    ax = gca; 
    set(ax , 'FontSize', 14,'FontWeight','bold','FontName', 'Times New Roman')
    ax.GridAlpha = 0.4;
    ax.GridColor = [0.65, 0.65, 0.65];
    ax.XTick = time_d;

    h = legend(lg{:});
    h.Location = 'northwest'; 
    h.FontSize = 14;
    h.Orientation = 'horizontal';
    h.EdgeColor = color{end};
    
    fs1 = strcat(outdir, 'MESH-MizuRoute-QI-51' ,'.fig');
    fs2 = strcat(outdir, 'MESH-MizuRoute-QI-51','.png');
    saveas(fig, fs1);
    saveas(fig, fs2);
    %close(fig);
    
    lg = {'QO_{71028585}','KWTRFF_{71028585}'};

    %subplot(3,1,2)
    % QO MESH & Miz RANK51
    fig = figure ('units','normalized','outerposition',[0 0 1 1]);
    h = plot(time(rs:rf), STFL(rs:rf , 51));
    h.LineStyle =  lsty{1};
    h.LineWidth = 2;
    h.Color = color{4};
    hold on
    h = plot(time(rs:rf), STFL_SM(rs:rf , 51, 4),'DatetimeTickFormat' , 'yyyy-MMM-dd');
    h.LineStyle =  lsty{2};
    h.LineWidth = 2;
    h.Color = color{4};
    
    % Axis Labels
    xlabel('\bf Time [hours]','FontSize',14,'FontName', 'Times New Roman');
    ylabel('\bf Flow rate [m^{3}/s]','FontSize',14,'FontName', 'Times New Roman');
    title('Outflow','FontSize',14,...
             'FontWeight','bold','FontName', 'Times New Roman')

    % Axis limit
    % xlimit
    xlim([time(rs) time(rf)])
    % Axis setting
    ax = gca; 
    set(ax , 'FontSize', 14,'FontWeight','bold','FontName', 'Times New Roman')
    ax.GridAlpha = 0.4;
    ax.GridColor = [0.65, 0.65, 0.65];
    ax.XTick = time_d;

    h = legend(lg{:});
    h.Location = 'northwest'; 
    h.FontSize = 14;
    h.Orientation = 'horizontal';
    h.EdgeColor = color{end};
    
    fs1 = strcat(outdir, 'MESH-MizuRoute-QO-51' ,'.fig');
    fs2 = strcat(outdir, 'MESH-MizuRoute-QO-51','.png');
    saveas(fig, fs1);
    saveas(fig, fs2);

    lg = {'RFF_{71028585}','basRFF_{71028585}'};
    %subplot(3,1,3)
    
    % RFF MESH & Miz RANK51
    fig = figure ('units','normalized','outerposition',[0 0 1 1]);
    h = plot(time(rs:rf), STFL_RFF(rs:rf , 51)*BA(51)/(3600*1000));
    h.LineStyle =  lsty{1};
    h.LineWidth = 2;
    h.Color = color{4};
    hold on
    h = plot(time(rs:rf), STFL_SM(rs:rf , 51, 1)*BA(51)/(3600*1000),'DatetimeTickFormat' , 'yyyy-MMM-dd');
    h.LineStyle =  lsty{2};
    h.LineWidth = 2;
    h.Color = color{4};
    
    % Axis Labels
    xlabel('\bf Time [hours]','FontSize',14,'FontName', 'Times New Roman');
    ylabel('\bf Flow rate [m^{3}/s]','FontSize',14,'FontName', 'Times New Roman');
    title('Runoff','FontSize',14,...
             'FontWeight','bold','FontName', 'Times New Roman')

    % Axis limit
    % xlimit
    xlim([time(rs) time(rf)])
    % Axis setting
    ax = gca; 
    set(ax , 'FontSize', 14,'FontWeight','bold','FontName', 'Times New Roman')
    ax.GridAlpha = 0.4;
    ax.GridColor = [0.65, 0.65, 0.65];
    ax.XTick = time_d;

    h = legend(lg{:});
    h.Location = 'northwest'; 
    h.FontSize = 14;
    h.Orientation = 'horizontal';
    h.EdgeColor = color{end};
    
    fs1 = strcat(outdir, 'MESH-MizuRoute-RFF-51' ,'.fig');
    fs2 = strcat(outdir, 'MESH-MizuRoute-RFF-51','.png');
    %saveas(fig, fs1);
    %saveas(fig, fs2);
    %close(fig);
    
%% display MESH and Summa files QO
    lg  = {'QO-WATROUTE','MizuRoute(KWTroutedRunoff)','MizuRoute(IRFroutedRunoff)'};
    outdir = 'output\BowBanff\QO\';
    for i = 1 : 2% : rk 
            fig = figure ('units','normalized','outerposition',[0 0 1 1]);

            h = plot(time, STFL(: , i),'DatetimeTickFormat' , 'yyyy-MMM');
            h.LineStyle =  lsty{1};
            h.LineWidth = 2;
            h.Color = color{1};
            hold on 
            h = plot(time, STFL_SM(: , i, 4));
            h.LineStyle =  lsty{1};
            h.LineWidth = 2;
            h.Color = color{3};
            
            h = plot(time, STFL_SM(: , i, 5));
            h.LineStyle =  lsty{1};
            h.LineWidth = 2;
            h.Color = color{4};
            
            grid on 

            % Axis Labels
            xlabel('\bf Time [hours]','FontSize',14,'FontName', 'Times New Roman');
            ylabel('\bf River Discharge [m^{3}/s]','FontSize',14,'FontName', 'Times New Roman');
            title(tl{i},'FontSize',14,...
                     'FontWeight','bold','FontName', 'Times New Roman')

            % Axis limit
            % xlimit
            xlim([time(1) time(end)])

            % Axis setting
            ax = gca; 
            set(ax , 'FontSize', 14,'FontWeight','bold','FontName', 'Times New Roman')
            ax.GridAlpha = 0.4;
            ax.GridColor = [0.65, 0.65, 0.65];
            ax.XTick = time_y;

            h = legend(lg{:});
            h.Location = 'northwest'; 
            h.FontSize = 14;
            h.Orientation = 'horizontal';
            h.EdgeColor = color{end};

            % save fig
            fs1 = strcat(outdir, tl{i} ,'.fig');
            fs2 = strcat(outdir, tl{i},'.png');
            % saveas(fig, fs1);
            % saveas(fig, fs2);
            % close(fig);
    end 

%% Display QI and sumUpstreamRunoff
lg  = {'QI-WATROUTE','MizuRoute(sumUpstreamRunoff)'};
    outdir = 'output\BowBanff\QI\';
    for i = 51 % : rk 
            fig = figure ('units','normalized','outerposition',[0 0 1 1]);

            h = plot(time(rs:rf), STFL_QI(rs:rf , i));
            h.LineStyle =  lsty{1};
            h.LineWidth = 2;
            h.Color = color{1};
            hold on 
            h = plot(time(rs:rf), STFL_SM(rs:rf , i, 3),'DatetimeTickFormat' , 'yyyy-MMM-dd');
            h.LineStyle =  lsty{2};
            h.LineWidth = 2;
            h.Color = color{3};
            
            grid on 

            % Axis Labels
            xlabel('\bf Time [hours]','FontSize',14,'FontName', 'Times New Roman');
            ylabel('\bf Flow rate entering the channel [m^{3}/s]','FontSize',14,'FontName', 'Times New Roman');
            title(tl{i},'FontSize',14,...
                     'FontWeight','bold','FontName', 'Times New Roman')

            % Axis limit
            % xlimit
            xlim([time(rs) time(rf)])

            % Axis setting
            ax = gca; 
            set(ax , 'FontSize', 14,'FontWeight','bold','FontName', 'Times New Roman')
            ax.GridAlpha = 0.4;
            ax.GridColor = [0.65, 0.65, 0.65];
            ax.XTick = time_d;

            h = legend(lg{:});
            h.Location = 'northwest'; 
            h.FontSize = 14;
            h.Orientation = 'horizontal';
            h.EdgeColor = color{end};

            % save fig
            fs1 = strcat(outdir, tl{i} ,'.fig');
            fs2 = strcat(outdir, tl{i},'.png');
%             saveas(fig, fs1);
%             saveas(fig, fs2);
            % close(fig);
    end

%% Display RFF and basRunoff     
    lg  = {'RFF-WATROUTE','MizuRoute(basRunoff)'};
    outdir = 'output\BowBanff\RFF\';
    for i = 1 %: rk
            fig = figure ('units','normalized','outerposition',[0 0 1 1]);

            h = plot(time, STFL_RFF(: , i),'DatetimeTickFormat' , 'yyyy-MMM');
            h.LineStyle =  lsty{1};
            h.LineWidth = 2;
            h.Color = color{1};
            hold on 
            h = plot(time, STFL_SM(: , i, 1));
            h.LineStyle =  lsty{2};
            h.LineWidth = 2;
            h.Color = color{2};
            
            grid on 

            % Axis Labels
            xlabel('\bf Time [hours]','FontSize',14,'FontName', 'Times New Roman');
            ylabel('\bf Total runoff [mm]','FontSize',14,'FontName', 'Times New Roman');
            title(tl{i},'FontSize',14,...
                     'FontWeight','bold','FontName', 'Times New Roman')

            % Axis limit
            % xlimit
            xlim([time(1) time(end)])

            % Axis setting
            ax = gca; 
            set(ax , 'FontSize', 14,'FontWeight','bold','FontName', 'Times New Roman')
            ax.GridAlpha = 0.4;
            ax.GridColor = [0.65, 0.65, 0.65];
            ax.XTick = time_y;

            h = legend(lg{:});
            h.Location = 'northwest'; 
            h.FontSize = 14;
            h.Orientation = 'horizontal';
            h.EdgeColor = color{end};

            % save fig
            fs1 = strcat(outdir, tl{i} ,'.fig');
            fs2 = strcat(outdir, tl{i},'.png');
%             saveas(fig, fs1);
%             saveas(fig, fs2);
            % close(fig);
    end    
%% Display RFF and sumUpstreamRunoff
    
    su_rff = STFL_SM(rs : rf , 1, 3);
    su_rff = (su_rff /BA(1))* (3600 * 1000);
    
    lg  = {'RFF-WATROUTE','MizuRoute(sumUpstreamRunoff-converted)'};
    outdir = 'output\BowBanff\RFF\su_rff\';
    
    fig = figure ('units','normalized','outerposition',[0 0 1 1]);
    
    for i = 1 
        h = plot(time(rs:rf), STFL_RFF(rs : rf, i),'DatetimeTickFormat' , 'yyyy-MMM');
        h.LineStyle =  lsty{1};
        h.LineWidth = 2;
        h.Color = color{1};
        hold on 

        %h = plot(time(rs:rf), STFL_SM(rs : rf , i, 3));
        h = plot(time(rs:rf), su_rff);
        h.LineStyle =  lsty{2};
        h.LineWidth = 2;
        h.Color = color{3};

        grid on 

        % Axis Labels
        xlabel('\bf Time [hours]','FontSize',14,'FontName', 'Times New Roman');
        ylabel('\bf Total runoff [mm]','FontSize',14,'FontName', 'Times New Roman');
        title(tl{i},'FontSize',14,...
                 'FontWeight','bold','FontName', 'Times New Roman')

        % Axis limit
        % xlimit
        xlim([time(rs) time(rf)])

        % Axis setting
        ax = gca; 
        set(ax , 'FontSize', 14,'FontWeight','bold','FontName', 'Times New Roman')
        ax.GridAlpha = 0.4;
        ax.GridColor = [0.65, 0.65, 0.65];
        ax.XTick = time_d;

        h = legend(lg{:});
        h.Location = 'northwest'; 
        h.FontSize = 14;
        h.Orientation = 'horizontal';
        h.EdgeColor = color{end};

        %save fig
        fs1 = strcat(outdir, tl{i} ,'.fig');
        fs2 = strcat(outdir, tl{i},'.png');
%         saveas(fig, fs1);
%         saveas(fig, fs2);
        %close(fig); 
    end
    
%% Plotting RFF from MESH and Summa 
    lg  = {'RFF-WATROUTE','RFF-WRrunoff'};
    outdir = 'output\BowBanff\RFF\WATROUTE_MIZ\';
    for i = 1
            fig = figure ('units','normalized','outerposition',[0 0 1 1]);

            h = plot(time(rs:rf), STFL_RFF(rs:rf , i),'DatetimeTickFormat' , 'yyyy-MMM');
            h.LineStyle =  lsty{1};
            h.LineWidth = 2;
            h.Color = color{1};
            hold on 
            h = plot(time(rs:rf), RFF_SM(rs:rf , i));
            h.LineStyle =  lsty{2};
            h.LineWidth = 2;
            h.Color = color{2};
            
            grid on 

            % Axis Labels
            xlabel('\bf Time [hours]','FontSize',14,'FontName', 'Times New Roman');
            ylabel('\bf Total runoff [mm]','FontSize',14,'FontName', 'Times New Roman');
            title(tl{i},'FontSize',14,...
                     'FontWeight','bold','FontName', 'Times New Roman')

            % Axis limit
            % xlimit
            xlim([time(rs) time(rf)])

            % Axis setting
            ax = gca; 
            set(ax , 'FontSize', 14,'FontWeight','bold','FontName', 'Times New Roman')
            ax.GridAlpha = 0.4;
            ax.GridColor = [0.65, 0.65, 0.65];
            ax.XTick = time_d;

            h = legend(lg{:});
            h.Location = 'northwest'; 
            h.FontSize = 14;
            h.Orientation = 'horizontal';
            h.EdgeColor = color{end};

            % save fig
            fs1 = strcat(outdir, tl{i} ,'.fig');
            fs2 = strcat(outdir, tl{i},'.png');
%             saveas(fig, fs1);
%             saveas(fig, fs2);
%             close(fig);
    end

end