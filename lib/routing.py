import os
import subprocess
import yaml
import json
import requests as req


def get_repo_root():
    """Get the root directory of the repo."""
    dir_in_repo = os.path.dirname(os.path.abspath('__file__'))  # os.getcwd()
    return subprocess.check_output('git rev-parse --show-toplevel'.split(),
                                   cwd=dir_in_repo,
                                   universal_newlines=True).rstrip()


ROOT_dir = get_repo_root()


def otp_build(otp_file=None, otp_folder=None, memory_gb=None):
    command_line = f'''java -Xmx{memory_gb}G -jar {otp_file} --build --save {otp_folder}'''
    # command_line = f'''java -Xmx{memory_gb}G -jar {otp_file} --cache {otp_folder} --basePath {otp_folder} --build {otp_folder}'''
    os.system(command_line)


def otp_server_starter(otp_file=None, otp_folder=None, memory_gb=None):
    # command_line = f'''java -Xmx{memory_gb}G -jar {otp_file} --build --save {otp_folder}'''
    # command_line = f'''java -Xmx{memory_gb}G -jar {otp_file} --build {otp_folder} --inMemory'''
    command_line = f'''java -Xmx{memory_gb}G -jar {otp_file} --load {otp_folder}'''
    os.system("start /B start cmd.exe @cmd /k " + command_line)


def req_define(fromPlace, toPlace, time, date, maxWalkDistance,
               numItineraries=1, clampInitialWait=0, mode="TRANSIT,WALK", arriveBy=False, bikeSpeed=25): # "TRANSIT,WALK"
    # fromPlace, toPlace: (59.33021, 18.07096)
    # numItineraries (int): 3
    # time (string): "5:00am"
    # date (string): "5-15-2019"
    # mode (string): "TRANSIT,WALK"
    # maxWalkDistance (int): 800 #meters
    # arriveBy (boolean): False
    otp_server = "http://localhost:8080/otp/routers/default/plan?"
    request = otp_server
    # places
    request += "fromPlace="
    request += str(fromPlace).strip(")").strip("(")
    request += "&toPlace="
    request += str(toPlace).strip(")").strip("(")
    # itinerary
    request += "&numItineraries="
    request += str(numItineraries)
    # clampInitialWait
    request += "&clampInitialWait="
    request += str(clampInitialWait)
    # time
    request += "&time="
    request += time
    # date
    request += "&date="
    request += date
    # mode
    request += "&mode="
    request += mode
    # maxWalkDistance
    request += "&maxWalkDistance="
    request += str(maxWalkDistance)
    # max ebike speed
    request += "&bikeSpeed="
    request += str(bikeSpeed)
    # arriveBy
    request += "&arriveBy="
    if arriveBy == False:
        request += "false"
    else:
        request += "true"

    return request


def requesting_origin_batch(data=None, walkdistance=300, folder2save=None, region=None, mode="BICYCLE,WALK"):
    origin = data.loc[:, 'origin'].values[0]
    print("Origin ID: ", origin, "# ODs", len(data))
    jsonList_ID = []
    def requesting(row):
        request = req_define(fromPlace=(row['lat_o'], row['lng_o']),
                             toPlace=(row['lat_d'], row['lng_d']),
                             time=row['depart_time'],
                             date=row['date'],
                             maxWalkDistance=walkdistance,
                             mode=mode)
        resp = req.get(request)
        output = resp.json()
        if "plan" in output:
            plan = output["plan"]["itineraries"][0]
            plan["Hour"] = row['depart_time']
            plan["Destination"] = row['destination']
            jsonList_ID.append(plan)
    data.apply(lambda row: requesting(row), axis=1)
    if len(jsonList_ID) > 0:
        with open(folder2save + region + '_origin_' + str(origin) + ".json", 'w') as outfile:
            for ele in jsonList_ID:
                print(json.dumps(ele), file=outfile)
