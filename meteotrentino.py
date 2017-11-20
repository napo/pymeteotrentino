# -*- coding: utf-8 -*-
"""
Created on Fri Dec 11 14:41:13 2015

@author: napo
"""
from __future__ import unicode_literals
from builtins import str as futureenc
import ckanapi
import datetime
import pytz
from lxml import etree
import requests
from geopy.geocoders import Nominatim
from geopy.distance import vincenty
import html2text 
urlbollettinostazione = "http://www.meteotrentino.it/bollettini/today/locali/Locali_REPLACE_it.xml"
urlbollettino = 'http://www.meteotrentino.it/bollettini/today/generale_it.xml'
urlstazioni = "http://dati.meteotrentino.it/service.asmx/listaStazioni"
bbox_trentino = (10.4521,46.5328,11.9627,45.6731)
urlsintetico = 'http://www.meteotrentino.it/bollettini/today/rss.xml'
urlvalanghe = 'http://www.meteotrentino.it/bollettini/today/valanghe_it.xml'
urldatitrentino = 'http://dati.trentino.it/'
urldatistazione = 'http://dati.meteotrentino.it/service.asmx/ultimiDatiStazione?codice='

class Stazione:
    codice = None
    nome = None
    nomebreve = None
    quota = None
    latitudine = None
    longitudine = None
    est = None
    north = None
    
    def getData(self):
        url = urldatistazione + self.codice
        r = requests.get(url)
        meteoxml = etree.fromstring(r.content)
        data = {}
        data['giorno'] = meteoxml[0].text
        data['temperaturaminima']= meteoxml[1].text
        data['temperaturamassima']= meteoxml[2].text
        data['pioggia']= meteoxml[3].text
        temperature = meteoxml[4]
        precipitazioni= meteoxml[5]
        venti = meteoxml[6]
        radiazione = meteoxml[7]  
        data['temperature']=temperature
        data['precipitazioni']=precipitazioni
        data['venti']=venti
        data['radiazione']= radiazione
        return data
#       
#   def getData(self):         
#       url = urldatistazione + self.codice
#       r = requests.get(url)
#       meteoxml = etree.fromstring(r.content)
#       data = {}
#       data['giorno'] = meteoxml[0].text
#       data['temperaturaminima']= meteoxml[1].text
#       data['temperaturamassima']= meteoxml[2].text
#       data['pioggia']= meteoxml[3].text
#       temperature = meteoxml[4]
#       precipitazioni= meteoxml[5]
#       venti = meteoxml[6]
#       radiazione = meteoxml[7]  
#       
#       return data
        
    
   

class StazioneBollettino:
    codice = None
    nome = None
    nomebreve = None
    quota = None
    latitudine = None
    longitudine = None
    est = None
    north = None
    meteoxml = None
    today = None
    oggi = None
    mattino = 0
    pomeriggio = 1

    def checkday(self):
        now = datetime.datetime.now(pytz.timezone('Europe/Rome'))
        oggi = "%s/%s/%s" % (now.day,now.month,now.year)
        
        if (self.oggi != oggi):
            self.today = datetime.datetime.now(pytz.timezone('Europe/Rome'))
            self.oggi = "%s/%s/%s" % (self.today.day,self.today.month,self.today.year)
            self.getBollettino()
            
        if self.meteoxml is None:
            self.getBollettino()       
            
    def getBollettino(self):
        if self.oggi is None:
            self.today = datetime.datetime.now(pytz.timezone('Europe/Rome'))
            self.oggi = "%s/%s/%s" % (self.today.day,self.today.month,self.today.year)           
        url = urlbollettinostazione.replace("REPLACE",self.codice)
        r = requests.get(url)
        self.meteoxml = etree.fromstring(r.content) #.find('evoluzione')     

    def infometeo(self,infosday,day):
        self.checkday()
        meteodata = []
        for info in infosday:
            data = {}
            data['giorno'] = day
            data['porzionegiorno'] = futureenc(info.find('porzionegiorno').text).lower()
            data['velocitavento'] = futureenc(info.find('ventovel').text).lower()
            data['direzionevento'] = futureenc(info.find('ventodir').text).lower()
            data['minima'] = futureenc(info.find('temperaturaminima').text).lower()
            data['massima'] = futureenc(info.find('temperaturamassima').text).lower()
            data['icona'] = futureenc(info.find('icona').text).lower()
            data['probprecitazioni'] = futureenc(info.find('probprec').text).lower()
            data['neve'] = futureenc(info.find('quotaneve').text).lower()
            if data['porzionegiorno']  == "none":
                data['porzionegiorno'] = ""
            if data['velocitavento']  == "none":
                data['velocitavento'] = ""
            if data['minima'] == 'none':
                data['minima'] = ""
            if data['massima']  == "none":
                data['massima'] = ""
            if data['icona']  == "none":
                data['icona'] = ""
            if data['neve'] == 'none':
                data['neve'] = ""
            if data['probprecitazioni'] == 'none':
                data['probprecitazioni'] = ""
            meteodata.append(data)
        return meteodata
        
    def evoluzione(self):
        self.checkday()
        evoluzione = futureenc(self.meteoxml.find('evoluzione').text)
        return evoluzione
    
    def meteo(self,days=0):
        if days > 4:
            return None
        self.checkday()
        sday = self.oggi
        if days > 0:
            delta = self.today + datetime.timedelta(days=days)
            sday = "%s/%s/%s" % (delta.day,delta.month,delta.year) 
        s = "giorno[@iddata='%s']" % (sday)
        infosday = self.meteoxml.findall(s)
        return self.infometeo(infosday,sday)
            
        
class Meteo:
    meteoxml = None
    valanghexml = None
    today = None
    stazioni = []
    bollettinilocali = []
    
    def listBollettiniLocali(self):
        codici = []
        datitrentino = ckanapi.RemoteCKAN(urldatitrentino,user_agent='ckanapiexample/1.0 (+http://example.com/my/website)')
        dati = datitrentino.action.package_show(id='bollettino-meteorologico-locale')
        resources = dati['resources']
        for resource in resources:        
            codice = resource['url'].replace("http://www.meteotrentino.it/bollettini/today/locali/Locali_","").replace("_it.xml","")
            codici.append(codice)
        return codici
            
    def checkday(self):
        now = datetime.datetime.now(pytz.timezone('Europe/Rome'))
        today = "%s/%s/%s" % (now.day,now.month,now.year)
        
        if (self.today != today):
            now = datetime.datetime.now(pytz.timezone('Europe/Rome'))
            self.today = "%s/%s/%s" % (now.day,now.month,now.year)
            self.getBollettino()
            
        if self.meteoxml is None:
            self.getBollettino()
            
    def __init__(self):
        now = datetime.datetime.now(pytz.timezone('Europe/Rome'))
        self.today = "%s/%s/%s" % (now.day,now.month,now.year)
        r = requests.get(urlstazioni)
        stazioni = etree.fromstring(r.content)
        for stazione in stazioni:
            s = Stazione()
            s.codice = stazione[0].text
            s.nome = stazione[1].text
            s.nomebreve = stazione[2].text
            s.quota = stazione[3].text
            s.latitudine = stazione[4].text
            s.logitudine = stazione[5].text
            s.est = stazione[6].text
            s.north = stazione[7].text
            self.stazioni.append(s)
        self.bollettinilocali = self.listBollettiniLocali()
        
    def sintetico(self):
        text = ""        
        r = requests.get(urlsintetico)
        rss = etree.fromstring(r.content)
        channel = rss.findall('channel')[0]
        summary = futureenc(channel.find('description').text).lower()
        title = futureenc(channel.find('item/title').text).lower()
        description = futureenc(channel.find('item/description').text)
        description = html2text.html2text(description)
        text = "%s %s\n%s\n%s" % (self.today, summary,title,description)
        return text

    def getBollettino(self):
        r = requests.get(urlbollettino)
        self.meteoxml = etree.fromstring(r.content)

    def getValanghe(self):
        r = requests.get(urlvalanghe)
        self.valanghexml = etree.fromstring(r.content)
        
    def evoluzionetempo(self):
        self.checkday()
        return self.meteoxml.find('EvoluzioneTempo').text

    def oggi(self):
        self.checkday()
        oggi = self.meteoxml.find('Oggi')   
        data = {}
        data['data'] = futureenc(oggi.find('Data').text).lower()
        data['descrizione'] = futureenc(oggi.find('CieloDesc').text).lower()
        data['precipitazioni'] = futureenc(oggi.find('PrecProb').text).lower()
        data['temporali'] = futureenc(oggi.find('TemporaliProb').text).lower()
        data['precestense'] = futureenc(oggi.find('PrecEstens').text).lower()
        data['precintense'] = futureenc(oggi.find('PrecInten').text).lower()
        data['temperature'] = futureenc(oggi.find('TempDesc').text).lower()
        data['temperaturamaxvalle'] = futureenc(oggi.find('TempMaxValle').text).lower()
        data['temperaturamaxquota'] = futureenc(oggi.find('TempMaxQuota').text).lower()
        data['venti'] = futureenc(oggi.find('VentiDesc').text).lower()
        data['ventoprovenienzaquota'] = futureenc(oggi.find('VentoProvQuota').text).lower()
        data['ventointesitaquota'] = futureenc(oggi.find('VentoIntenQuota').text).lower()
        data['ventoprovenienzavalle'] = futureenc(oggi.find('VentoProvValle').text).lower()
        data['ventointesitavalle'] = futureenc(oggi.find('VentoIntenValle').text).lower()
        data['imgtrentino'] = futureenc(oggi.find('imgtrentino').text).lower()    
        data['desciconanw'] = futureenc(oggi.find('desciconaNW').text).lower()    
        data['desciconane'] = futureenc(oggi.find('desciconaNE').text).lower()    
        data['desciconas'] = futureenc(oggi.find('desciconaS').text).lower()    
        data['iconanw'] = futureenc(oggi.find('iconaNW').text).lower()   
        data['iconane'] = futureenc(oggi.find('iconaNE').text).lower()  
        data['iconas'] = futureenc(oggi.find('iconaS').text).lower()  
        return data
        
    def domani(self):
        self.checkday()
        domani = self.meteoxml.find('Domani') 
        data = {}
        data['data'] = futureenc(domani.find('Data').text).lower()
        data['descrizione'] = futureenc(domani.find('CieloDesc').text).lower()
        data['precipitazioni'] = futureenc(domani.find('PrecipProb').text).lower()
        data['temporali'] = futureenc(domani.find('TemporaliProb').text).lower()
        data['precestense'] = futureenc(domani.find('PrecEstens').text).lower()
        data['precintense'] = futureenc(domani.find('PrecInten').text).lower()
        data['temperature'] = futureenc(domani.find('TempDesc').text).lower()
        data['temperaturaminvalle'] = futureenc(domani.find('TempMinValle').text).lower()
        data['temperaturaminquota'] = futureenc(domani.find('TempMinQuota').text).lower()
        data['temperaturamaxvalle'] = futureenc(domani.find('TempMaxValle').text).lower()
        data['temperaturamaxquota'] = futureenc(domani.find('TempMaxQuota').text).lower()
        data['zerotermico00'] = futureenc(domani.find('ZeroTermico00').text).lower()
        data['zerotermico12'] = futureenc(domani.find('ZeroTermico12').text).lower()
        data['venti'] = futureenc(domani.find('VentiDesc').text).lower()
        data['ventovalleprovenienza'] = futureenc(domani.find('VentoValleProv').text).lower()
        data['ventovalleintesita'] = futureenc(domani.find('VentoValleInten').text).lower()
        data['ventoquotaprovenienza'] = futureenc(domani.find('VentoQuotaProv').text).lower()
        data['ventoquotaintesita'] = futureenc(domani.find('VentoQuotaInten').text).lower()
        data['imgtrentino'] = futureenc(domani.find('imgtrentino').text).lower()
        data['desciconanw00'] = futureenc(domani.find('desciconaNW00').text).lower()
        data['desciconane00'] = futureenc(domani.find('desciconaNE00').text).lower()
        data['desciconas00'] = futureenc(domani.find('desciconaS00').text).lower()
        data['iconanw00'] = futureenc(domani.find('iconaNW00').text).lower()
        data['iconane00'] = futureenc(domani.find('iconaNE00').text).lower()
        data['iconas00'] = futureenc(domani.find('iconaS00').text).lower()
        data['imgtrentino2'] = futureenc(domani.find('imgtrentino2').text).lower()
        data['desciconanw12'] = futureenc(domani.find('desciconaNW12').text).lower()
        data['desciconane12'] = futureenc(domani.find('desciconaNE12').text).lower()
        data['desciconas12'] = futureenc(domani.find('desciconaS12').text).lower()
        data['iconanw12'] = futureenc(domani.find('iconaNW12').text).lower()
        data['iconane12'] = futureenc(domani.find('iconaNE12').text).lower()
        data['iconas12'] = futureenc(domani.find('iconaS12').text).lower()
        return data

    def dopodomani(self):
        self.checkday()
        dopodomani = self.meteoxml.find('DopoDomani') 
        data = {}
        data['data'] = futureenc(dopodomani.find('Data').text).lower()
        data['descrizione'] = futureenc(dopodomani.find('CieloDesc').text).lower()
        data['precipitazioni'] = futureenc(dopodomani.find('PrecipProb').text).lower()
        data['temporali'] = futureenc(dopodomani.find('TemporaliProb').text).lower()
        data['precestense'] = futureenc(dopodomani.find('PrecEstens').text).lower()
        data['precintense'] = futureenc(dopodomani.find('PrecInten').text).lower()
        data['temperature'] = futureenc(dopodomani.find('TempDesc').text).lower()
        data['temperaturaminvalle'] = futureenc(dopodomani.find('TempMinValle').text).lower()
        data['temperaturaminquota'] = futureenc(dopodomani.find('TempMinQuota').text).lower()
        data['temperaturamaxvalle'] = futureenc(dopodomani.find('TempMaxValle').text).lower()
        data['temperaturamaxquota'] = futureenc(dopodomani.find('TempMaxQuota').text).lower()
        data['zerotermico00'] = futureenc(dopodomani.find('ZeroTermico00').text).lower()
        data['zerotermico12'] = futureenc(dopodomani.find('ZeroTermico12').text).lower()
        data['venti'] = futureenc(dopodomani.find('VentiDesc').text).lower()
        data['ventovalleprovenienza'] = futureenc(dopodomani.find('VentoValleProv').text).lower()
        data['ventovalleintesita'] = futureenc(dopodomani.find('VentoValleInten').text).lower()
        data['ventoquotaprovenienza'] = futureenc(dopodomani.find('VentoQuotaProv').text).lower()
        data['ventoquotaintesita'] = futureenc(dopodomani.find('VentoQuotaInten').text).lower()
        data['imgtrentino'] = futureenc(dopodomani.find('imgtrentino').text).lower()
        data['desciconanw00'] = futureenc(dopodomani.find('desciconaNW00').text).lower()
        data['desciconane00'] = futureenc(dopodomani.find('desciconaNE00').text).lower()
        data['desciconas00'] = futureenc(dopodomani.find('desciconaS00').text).lower()
        data['iconanw00'] = futureenc(dopodomani.find('iconaNW00').text).lower()
        data['iconane00'] = futureenc(dopodomani.find('iconaNE00').text).lower()
        data['iconas00'] = futureenc(dopodomani.find('iconaS00').text).lower()
        data['imgtrentino2'] = futureenc(dopodomani.find('imgtrentino2').text).lower()
        data['desciconanw12'] = futureenc(dopodomani.find('desciconaNW12').text).lower()
        data['desciconane12'] = futureenc(dopodomani.find('desciconaNE12').text).lower()
        data['desciconas12'] = futureenc(dopodomani.find('desciconaS12').text).lower()
        data['iconanw12'] = futureenc(dopodomani.find('iconaNW12').text).lower()
        data['iconane12'] = futureenc(dopodomani.find('iconaNE12').text).lower()
        data['iconas12'] = futureenc(dopodomani.find('iconaS12').text).lower()
        return data
        
    def giornisuccessivi(self):
        self.checkday()
        successivi = self.meteoxml.findall('GiorniSuccessivi') 
        giorni = []
        for successivo in successivi:
            data = {}
            data['data'] = futureenc(successivo.find('Data').text).lower()
            data['descrizione'] = futureenc(successivo.find('CieloDesc').text).lower()
            data['precipitazioni'] = futureenc(successivo.find('PrecipProb').text).lower()
            data['temporali'] = futureenc(successivo.find('TemporaliProb').text).lower()
            data['precestense'] = futureenc(successivo.find('PrecEstens').text).lower()
            data['precintense'] = futureenc(successivo.find('PrecInten').text).lower()
            data['temperaturamaxvalle'] = futureenc(successivo.find('TempMaxValle').text).lower()
            data['temperaturaminvalle'] = futureenc(successivo.find('TempMinValle').text).lower()
            data['zerotermico12'] = futureenc(successivo.find('ZeroTermico12').text).lower()
            data['ventovalleprovenienza00'] = futureenc(successivo.find('VentoValleProv00').text).lower()
            data['ventovalleintesita00'] = futureenc(successivo.find('VentoValleInten00').text).lower()
            data['descicona'] = futureenc(successivo.find('descicona').text).lower()
            data['icona'] = futureenc(successivo.find('icona').text).lower()
            giorni.append(data)
        return giorni

    def findStazioneBollettino(self,lat,lon):
        stazione = None
        location = (lat,lon)
        rdistance = 40075 #lunghezza equatore in metrei
        for s in self.stazioni:
            if (s.codice in self.bollettinilocali):
                sloc = (s.latitudine,s.logitudine)
                distance = (vincenty(location, sloc).kilometers)
                if (rdistance > distance):
                    rdistance = distance
                    sb = StazioneBollettino()
                    sb.codice = s.codice
                    sb.latitudine = s.latitudine
                    sb.longitudine = s.logitudine
                    sb.nome = s.nome
                    sb.nomebreve = s.nomebreve
                    sb.quota = s.quota
                    sb.est = s.est
                    sb.north = s.north
                    stazione = sb
        return stazione
        
    def findStazione(self,lat,lon):
        stazione = None
        location = (lat,lon)
        rdistance = 40075 #lunghezza equatore in metrei
        for s in self.stazioni:
            sloc = (s.latitudine,s.logitudine)
            distance = (vincenty(location, sloc).kilometers)
            if (rdistance > distance):
                rdistance = distance
                stazione = s
        return stazione

    def findStazioneBollettinoByAddress(self,address):
         geolocator = Nominatim(country_bias="It",view_box=bbox_trentino)
         address = unicode(address, 'utf-8') #address.encode('utf-8')
         address = address.lower()
         if address.find("trentino") == -1:
             address += ", trentino"
         location = geolocator.geocode(address)
         return self.findStazioneBollettino(location.latitude, location.longitude)
         
    def findStazioneByAddress(self,address):
         geolocator = Nominatim(country_bias="It",view_box=bbox_trentino)
         address = unicode(address, 'utf-8') #address.encode('utf-8')
         address = address.lower()
         if address.find("trentino") == -1:
             address += ", trentino"
         location = geolocator.geocode(address)
         return self.findStazione(location.latitude, location.longitude)
        

        