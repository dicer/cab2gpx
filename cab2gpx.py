#!/usr/bin/python
import subprocess
import re
import argparse
import json
import codecs
from xml.sax.saxutils import escape

#color of the gpx points
COLOR  = "#f9d4d4"


def download(kwargs):

  cmd = "curl \'https://www.callabike-interaktiv.de/kundenbuchung/hal2ajax_process.php?callback=jQuery\' -H \'Host: www.callabike-interaktiv.de\' -H \'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0\' -H \'Accept: text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01\' -H \'Accept-Language: en-US,en;q=0.5\' --compressed -H \'Referer: https://www.callabike-interaktiv.de/kundenbuchung/process.php?proc=bikesuche&f=500&\' -H \'Content-Type: application/x-www-form-urlencoded; charset=UTF-8\' -H \'X-Requested-With: XMLHttpRequest\' -H \'Cookie: fe_typo_user=13; _skey=23; PHPSESSID=42\' -H \'Connection: keep-alive\' --data \'zoom=10&lng1=&lat1=&lng2=&lat2=&stadtCache=&mapstation_id=&mapstadt_id={0}&verwaltungfirma=&searchmode=default&with_staedte=N&buchungsanfrage=N&bereich=2&stoinput=&before=&after=&ajxmod=hal2map&callee=getMarker&requester=bikesuche&key=&webfirma_id=500\'".format(kwargs.city)
  #print cmd

  data = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read().strip()
  data = re.sub(r'^jQuery\(', '', data)
  data = re.sub(r'\)$', '', data)
  #print data

  jsonData = json.loads(unicode(data, "utf-8"), "utf-8")

  osmFile = codecs.open(kwargs.output,"w","utf-8")
  #header
  osmFile.write("<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>\n")
  osmFile.write("<gpx version=\"1.1\" creator=\"cab2gpx\" xmlns=\"http://www.topografix.com/GPX/1/1\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd\">\n")

  print "Found {0} markers".format(len(jsonData["marker"]))
  skippedStations=0
  for place in jsonData["marker"]:
    name = re.sub(r'&nbsp;', ' ', place["hal2option"]["tooltip"])

    #filter temporary markers
    if len(place["hal2option"]["standort_id"]) == 0 or place["iconName"] == "bikeicon":
      #print u"Skipping {0}".format(name)
      skippedStations = skippedStations + 1
      continue

    osmFile.write("  <wpt lat='{0}' lon='{1}'>\n".format(place["lat"], place["lng"]))
    osmFile.write(u"    <name>{0}</name>\n".format(u'\U0001F6B2'))
    osmFile.write(u"    <desc>{0}\n\n".format(escape(name)))
    osmFile.write(u"    </desc>\n")
    osmFile.write("     <type>{0}</type>\n".format(escape(place["hal2option"]["objecttyp"])))
    osmFile.write("     <extensions>\n")
    osmFile.write("       <color>{0}</color>\n".format(COLOR))
    osmFile.write("     </extensions>\n")
    osmFile.write("  </wpt>\n")

  osmFile.write("</gpx>")
  osmFile.close()

  print u"Skipping {0} stations because they are temporary".format(skippedStations)


def listcities():
  cmd = "curl \'https://www.callabike-interaktiv.de/kundenbuchung/hal2ajax_process.php?callback=jQuery\' -H \'Host: www.callabike-interaktiv.de\' -H \'User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0\' -H \'Accept: text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01\' -H \'Accept-Language: en-US,en;q=0.5\' --compressed -H \'Referer: https://www.callabike-interaktiv.de/kundenbuchung/process.php?proc=bikesuche&f=500&&f=500\' -H \'Content-Type: application/x-www-form-urlencoded; charset=UTF-8\' -H \'X-Requested-With: XMLHttpRequest\' -H \'Cookie: fe_typo_user=5; _skey=23; PHPSESSID=42\' -H \'Connection: keep-alive\' -H \'Cache-Control: max-age=0\' --data \'zoom=10&lng1=&lat1=&lng2=&lat2=&stadtCache=&mapstation_id=&mapstadt_id=&verwaltungfirma=&searchmode=default&with_staedte=J&ajxmod=hal2map&callee=getMarker&before=&after=&requester=bikesuche&key=&webfirma_id=500\'"

  data = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.read().strip()
  data = re.sub(r'^jQuery\(', '', data)
  data = re.sub(r'\)$', '', data)

  jsonData = json.loads(unicode(data, "utf-8"), "utf-8")
  
  for place in jsonData["marker"]:
    name = re.sub(r'&nbsp;', ' ', place["hal2option"]["tooltip"])
    cityId = re.sub(r'^s', '', place["hal2option"]["id"])
    print u"{0} - {1}".format(cityId, name)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get Call a bike stations for a certain city as GPX file.', version='%(prog)s 1.0')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-l', '--listcities', help='List all the city ids that are available', action="store_true")
    group.add_argument('-c', '--city', type=int, help='Download for this city id')

    parser.add_argument('-o', '--output',type=str, default='export.gpx', help='output file to write to')
    args = parser.parse_args()

    if (args.listcities):
      listcities()
    else:
      download(args)
