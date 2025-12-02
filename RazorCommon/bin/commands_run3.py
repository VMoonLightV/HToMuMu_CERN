import os
import sys

sys.path.append('../../condor/utils')
import version as v


version = 'v39'
golden_json_path = os.getenv("CMSSW_BASE") + "/src/HToMuMu/RazorCommon/data/Run3/"
json = {
        '2022':'Cert_Collisions2022_355100_362760_Golden.json',
        '2023':'Cert_Collisions2023_366442_370790_Golden.json',
        '2024':'Cert_Collisions2024_378981_386951_Golden.json',
        }

data_path = f'/eos/uscms/store/group/lpchmumu/esledge/analyzer_HiggsMuMu_{v.ANALYZER_VERSION_NUMBER}/Data/'

analyzer_output_files = [file for file in os.listdir(data_path) if "Higgs" in file]
for era in os.listdir(data_path):
        year = era.split("_")[1][:4]
        print("Processing era: " + era)
        if(year != '2025'): cert = golden_json_path + json[year]
        else:
                print("No Golden JSON file exists for 2025")
                continue

        analyzer_output_files = [file for file in os.listdir(data_path + era) if "Higgs" in file]

        current_file = 0
        total_files = len(analyzer_output_files)
        for analyzer_file in analyzer_output_files:
                current_file +=1
                print(f"Processing file {current_file} of {total_files}")
                output_file = analyzer_file[:-5]+'_goodLumi.root'
                if os.path.isfile(data_path + era + '/' + output_file):
                        print("A goodLumi file already exists. SKIPPING")
                        continue
                
                os.system("sed -i \"/JSONfile =/c\JSONfile = \'{}\'\" ../python/loadJson.py".format(cert))
                os.system("FWLiteGoodLumi ../python/loadJson.py {} {}".format(data_path + era + '/' + analyzer_file, output_file))
                os.system("cp {} {}/{}".format(output_file, data_path + era, output_file))
                if os.path.isfile(data_path + era + '/' + output_file):
                        print("SUCCESS") 
                        os.system("rm {}".format(output_file))
                        #quit()
                else: print("SOMETHING WENT WRONG")
                if not os.path.isfile(data_path + era + '/' + output_file):
                        print("No goodLumi file was created for era: {} | file: {}".format(era, data_path + era + '/' + output_file)) 
                        break
