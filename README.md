# pymeteotrentino
python class for the xml of meteotrentino.it

## note
actual support only italian language

# how use it

```
import meteotrentino
m = meteotrentino.Meteo()
# mostra sintesi del giorno
print m.sintetico()
```
13/12/2015 previsioni sintetiche a 5 giorni
evoluzione
Oggi, domenica, nubi alte con formazione di locali foschie o banchi di nebbia dalla sera. Lunedì e martedì soleggiato con qualche nube alta e formazione di locali foschie o banchi di nebbia nelle ore più fredde. Mercoledì parzialmente soleggiato. Giovedì soleggiato.  

Previsioni
dom 13/12 Nuvoloso Temperature Trento -7/5°C  
lun 14/12 Poco nuvoloso Temperature Trento -5/5°C  
mar 15/12 Poco nuvoloso Temperature Trento -8/5°C  
mer 16/12 Nuvoloso Temperature Trento -7/7°C  
gio 17/12 Poco nuvoloso Temperature Trento -7/7°C 

```
# bolettino di oggi
print m.oggi()
```
{u'venti': u'deboli variabili.', u'ventoprovenienzavalle': u'variabile', u'temperature': u'massime senza notevoli variazioni.', u'temporali': u'molto bassa', u'desciconanw': u'nuvoloso', u'iconanw': u'http://www.meteotrentino.it/bollettini/today/icometeo/ico19_0_0.png', u'temperaturamaxquota': u'9', u'precestense': u'isolati/e', u'desciconas': u'nuvoloso', u'descrizione': u'  soleggiato con temporanei annuvolamenti e formazione di locali foschie o banchi di nebbia dalla sera.', u'temperaturamaxvalle': u'5', u'iconane': u'http://www.meteotrentino.it/bollettini/today/icometeo/ico19_0_0.png', u'desciconane': u'nuvoloso', u'precintense': u'debole', u'ventoprovenienzaquota': u'variabile', u'ventointesitaquota': u'debole', u'iconas': u'http://www.meteotrentino.it/bollettini/today/icometeo/ico19_0_0.png', u'data': u'13/12/2015', u'imgtrentino': u'http://www.meteotrentino.it/bollettini/today/img/generale/imgoggi_it.png', u'precipitazioni': u'molto bassa', u'ventointesitavalle': u'debole'}
```
# cerca la stazione meteo più vicina ad una coppia di coordinate
s = m.findStazione(46.06855,11.12349)
print "%s %s" % (s.nome,s.codice)
```
Trento (Piazza Vittoria) T0137
```

