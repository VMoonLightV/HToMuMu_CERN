import os

version = 'v39'
golden_json_path = os.getenv("CMSSW_BASE") + "/src/HToMuMu/RazorCommon/data/Run3/"
json = {
        '2022':'Cert_Collisions2022_355100_362760_Golden.json',
        '2023':'Cert_Collisions2023_366442_370790_Golden.json',
        '2024':'Cert_Collisions2024_378981_386951_Golden.json',
        }

data_path = '/eos/uscms/store/group/lpchmumu/esledge/analyzer_HiggsMuMu_v1.1/Data/'
for era in os.listdir(data_path):
        year = era.split("_")[1][:4]
        print("Processing era: " + era)
        if(year != '2025'): cert = golden_json_path + json[year]
        else:
                print("No Golden JSON file exists for 2025")
                continue
        if os.path.isfile(data_path + era + '/' + "*_goodLumi.root"):
                print("goodLumi file already exists. SKIPPING") 
                continue
                
        for rootFile in os.listdir(data_path + era):
                if("SumGenWeight" not in rootFile):
                        continue
                output_file = rootFile[:-5]+'_goodLumi.root'
                os.system("sed -i \"/JSONfile =/c\JSONfile = \'{}\'\" ../python/loadJson.py".format(cert))
                os.system("FWLiteGoodLumi ../python/loadJson.py {} {}".format(data_path + era + '/' + rootFile, output_file))
                os.system("cp {} {}/{}".format(output_file, data_path + era, output_file))
                if os.path.isfile(data_path + era + '/' + output_file):
                        print("SUCCESS") 
                        os.system("rm {}".format(output_file))
                else: print("SOMETHING WENT WRONG")
        if not os.path.isfile(data_path + era + '/' + output_file):
                print("No goodLumi file was created for era: {} | file: {}".format(era, data_path + era + '/' + output_file)) 
                break
