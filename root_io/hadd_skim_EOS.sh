EOS_PATH="/eos/home-y/yulou/Fnal-hmm/hmm-skims/VBF/"

##############  2022  ##############
hadd background_2022_skim_Full.root ${EOS_PATH}DY_2022_skim.root ${EOS_PATH}EWK_2022_skim.root ${EOS_PATH}TT_2022_skim.root DiBoson_2022_skim.root
hadd background_2022_skim_NoDY50.root ${EOS_PATH}DY120to200_2022_skim.root ${EOS_PATH}EWK_2022_skim.root ${EOS_PATH}TT_2022_skim.root DiBoson_2022_skim.root

hadd signal_2022_skim_Full.root ${EOS_PATH}ggH_2022_skim.root ${EOS_PATH}VBF_2022_skim.root ${EOS_PATH}ttH_2022_skim.root
hadd signal_2022_skim_NottH.root ${EOS_PATH}ggH_2022_skim.root ${EOS_PATH}VBF_2022_skim.root

##############  2022EE  ##############
hadd background_2022EE_skim_Full.root ${EOS_PATH}DY_2022EE_skim.root ${EOS_PATH}EWK_2022EE_skim.root ${EOS_PATH}TT_2022EE_skim.root DiBoson_2022EE_skim.root
hadd background_2022EE_skim_NoDY50.root ${EOS_PATH}DY120to200_2022EE_skim.root ${EOS_PATH}EWK_2022EE_skim.root ${EOS_PATH}TT_2022EE_skim.root DiBoson_2022EE_skim.root

hadd signal_2022EE_skim_Full.root ${EOS_PATH}ggH_2022EE_skim.root ${EOS_PATH}VBF_2022EE_skim.root ${EOS_PATH}ttH_2022EE_skim.root
hadd signal_2022EE_skim_NottH.root ${EOS_PATH}ggH_2022EE_skim.root ${EOS_PATH}VBF_2022EE_skim.root

##############  2022Combined  ##############
hadd background_2022Combined_skim_Full.root background_2022_skim_Full.root background_2022EE_skim_Full.root
hadd background_2022Combined_skim_NoDY50.root background_2022_skim_NoDY50.root background_2022EE_skim_NoDY50.root

hadd signal_2022Combined_skim_Full.root signal_2022_skim_Full.root signal_2022EE_skim_Full.root
hadd signal_2022Combined_skim_NottH.root signal_2022_skim_NottH.root signal_2022EE_skim_NottH.root

##############  2023  ##############
hadd background_2023_skim_Full.root ${EOS_PATH}DY_2023_skim.root ${EOS_PATH}EWK_2023_skim.root ${EOS_PATH}TT_2023_skim.root DiBoson_2023_skim.root
hadd background_2023_skim_NoDY50.root ${EOS_PATH}DY120to200_2023_skim.root ${EOS_PATH}EWK_2023_skim.root ${EOS_PATH}TT_2023_skim.root DiBoson_2023_skim.root

hadd signal_2023_skim_Full.root ${EOS_PATH}ggH_2023_skim.root ${EOS_PATH}VBF_2023_skim.root ${EOS_PATH}ttH_2023_skim.root
hadd signal_2023_skim_NottH.root ${EOS_PATH}ggH_2023_skim.root ${EOS_PATH}VBF_2023_skim.root

##############  2023BPix  ##############
hadd background_2023BPix_skim_Full.root ${EOS_PATH}DY_2023BPix_skim.root ${EOS_PATH}EWK_2023BPix_skim.root ${EOS_PATH}TT_2023BPix_skim.root DiBoson_2023BPix_skim.root
hadd background_2023BPix_skim_NoDY50.root ${EOS_PATH}DY120to200_2023BPix_skim.root ${EOS_PATH}EWK_2023BPix_skim.root ${EOS_PATH}TT_2023BPix_skim.root DiBoson_2023BPix_skim.root

hadd signal_2023BPix_skim_Full.root ${EOS_PATH}ggH_2023BPix_skim.root ${EOS_PATH}VBF_2023BPix_skim.root ${EOS_PATH}ttH_2023BPix_skim.root
hadd signal_2023BPix_skim_NottH.root ${EOS_PATH}ggH_2023BPix_skim.root ${EOS_PATH}VBF_2023BPix_skim.root

##############  2023Combined  ##############
hadd background_2023Combined_skim_Full.root background_2023_skim_Full.root background_2023BPix_skim_Full.root
hadd background_2023Combined_skim_NoDY50.root background_2023_skim_NoDY50.root background_2023BPix_skim_NoDY50.root

hadd signal_2023Combined_skim_Full.root signal_2023_skim_Full.root signal_2023BPix_skim_Full.root
hadd signal_2023Combined_skim_NottH.root signal_2023_skim_NottH.root signal_2023BPix_skim_NottH.root

##############  2024 ##############
#hadd background_2024_skim_Full.root DY_2024_skim.root

#hadd signal_2023BPix_skim_Full.root ggH_2023BPix_skim.root VBF_2023BPix_skim.root ttH_2023BPix_skim.root
#hadd signal_2023BPix_skim_NottH.root ggH_2023BPix_skim.root VBF_2023BPix_skim.root


##############  Combined  ##############
hadd background_Combined_skim_Full.root background_2022Combined_skim_Full.root background_2023Combined_skim_Full.root 
hadd background_Combined_skim_NoDY50.root background_2022Combined_skim_NoDY50.root background_2023Combined_skim_NoDY50.root 

hadd signal_Combined_skim_Full.root signal_2022Combined_skim_Full.root signal_2023Combined_skim_Full.root
hadd signal_Combined_skim_NottH.root signal_2022Combined_skim_NottH.root signal_2023Combined_skim_NottH.root

hadd Data_Combined_skim.root Data_2022EE_skim.root Data_2022_skim.root Data_2023BPix_skim.root Data_2023_skim.root 

