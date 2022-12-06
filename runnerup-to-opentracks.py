import sqlite3
from datetime import datetime
import os


def write_gpx(i):
    sql = f'select * from activity where _id = {i} and deleted = 0;'
    res = cur.execute(sql)
    activity_status = res.fetchall()
    
    activity_types = {0:'run', 1:'bike', 4:'walk'}
    (_id, start_time, distance, time, name, comment, num_type) = (activity_status[0][:7])
    
    cdata = (str(datetime.fromtimestamp(start_time).strftime("%Y-%m-%dT%H:%M"))+
        str(datetime.now().astimezone().tzinfo))  
    name = (str(datetime.fromtimestamp(start_time).strftime("%Y-%m-%d_%H_%M_%S.%f")[:-3])+
            str(datetime.fromtimestamp(start_time).strftime("_%Y-%m-%dT%H_%M")+
            str(datetime.now().astimezone().tzinfo)))
    track_id = hash(cdata)
    
    file = open(name + '.gpx', 'x')
    
    
    type_location = 3
    longitude = cur.execute(f'select longitude from location where activity_id ={i} and type={type_location};').fetchall()
    latitude = cur.execute(f'select latitude from location where activity_id ={i} and type={type_location};').fetchall()
    altitude = cur.execute(f'select altitude from location where activity_id ={i} and type={type_location};').fetchall()
    timer = cur.execute(f'select time from location where activity_id ={i} and type={type_location};').fetchall()
    dist = cur.execute(f'select distance from location where activity_id ={i} and type={type_location};').fetchall()
    accurancy = cur.execute(f'select accurancy from location where activity_id ={i} and type={type_location};').fetchall()
    max_speed = None
    
    head_gpx =f"""<?xml version="1.0" encoding="UTF-8"?>
<gpx
version=""
creator="OpenTracks (imported from RunnerUp with runnerup-to-opentracks.py)"
xmlns="http://www.topografix.com/GPX/1/1"
xmlns:topografix="http://www.topografix.com/GPX/Private/TopoGrafix/0/1"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
xmlns:opentracks="http://opentracksapp.com/xmlschemas/v1"
xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v2"
xmlns:gpxtrkx="http://www.garmin.com/xmlschemas/TrackStatsExtension/v1"
xmlns:cluetrust="http://www.cluetrust.com/Schemas/"
xmlns:pwr="http://www.garmin.com/xmlschemas/PowerExtension/v1"
xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.topografix.com/GPX/Private/TopoGrafix/0/1 http://www.topografix.com/GPX/Private/TopoGrafix/0/1/topografix.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v2 https://www8.garmin.com/xmlschemas/TrackPointExtensionv2.xsd http://www.garmin.com/xmlschemas/PowerExtension/v1 https://www8.garmin.com/xmlschemas/PowerExtensionv1.xsd http://www.garmin.com/xmlschemas/TrackStatsExtension/v1 http://www.cluetrust.com/Schemas http://www.cluetrust.com/Schemas/gpxdata10.xsd http://opentracksapp.com/xmlschemas/v1 http://opentracksapp.com/xmlschemas/OpenTracks_v1.xsd">
<trk>
<name><![CDATA[{cdata}]]></name>
<desc><![CDATA[]]></desc>
<type><![CDATA[{activity_types[num_type]}]]></type>
<extensions>
<topografix:color>c0c0c0</topografix:color>
<opentracks:trackid>{track_id}</opentracks:trackid>
<gpxtrkx:TrackStatsExtension>
<gpxtrkx:Distance>{distance}</gpxtrkx:Distance>
<gpxtrkx:TimerTime>{time}</gpxtrkx:TimerTime>
<gpxtrkx:MovingTime>{time}</gpxtrkx:MovingTime>
<gpxtrkx:StoppedTime>null</gpxtrkx:StoppedTime>
<gpxtrkx:MaxSpeed>{max_speed}</gpxtrkx:MaxSpeed>
<gpxtrkx:Ascent>null</gpxtrkx:Ascent>
<gpxtrkx:Descent>null</gpxtrkx:Descent>
</gpxtrkx:TrackStatsExtension>
</extensions>
<trkseg>""" 
    file.write(head_gpx)
    
    for i in range(1, len(longitude)): 
        speed_i = round((dist[i][0]-dist[i-1][0])/(timer[i][0]-timer[i-1][0])*1000, 2)
        time_i = datetime.utcfromtimestamp((timer[i][0])//1000).astimezone().replace(microsecond=0).isoformat()
        body_gpx = f"""
<trkpt lat="{latitude[i][0]}" lon="{longitude[i][0]}">
<ele>{round(altitude[i][0],1)}</ele>
<time>{time_i}</time>
<extensions><gpxtpx:TrackPointExtension>
<gpxtpx:speed>{speed_i}</gpxtpx:speed>
<opentracks:accuracy_horizontal>{round(accurancy[i][0],2)}</opentracks:accuracy_horizontal></gpxtpx:TrackPointExtension></extensions>
</trkpt>"""
        file.write(body_gpx)
        
    tail_gpx = """
</trkseg>
</trk>
</gpx>"""
    file.write(tail_gpx)
    file.close()
    print(name)

if __name__ == "__main__":
    for f in os.listdir('.'):
        if f.endswith('.db.export'):
            try:
                con = sqlite3.connect(f)
                cur = con.cursor()
                print('DB init')
                sql = 'select _id from activity where deleted = 0;'
                res = cur.execute(sql)
                activity_id = res.fetchall()
                
                for _id in activity_id:
                    write_gpx(_id[0])
                
            except:
                print("DB exit")
