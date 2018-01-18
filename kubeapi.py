#!/usr/bin/python3
from datetime import datetime, date, time
import json
import requests
import time
import sys
import re

sall=0
dall=0
nall=0
nsall=0
dsall=0
dim=0
role=""
ip=""
if len(sys.argv) < 3:
  if len(sys.argv) == 2:
    if str(sys.argv[1]) == "full":
      sall=1
    elif str(sys.argv[1]) == "nodes":
      nall=1
    else:
      print("No enough arguments")
      sys.exit(1)
  else:
    print("No enough arguments")
    sys.exit(1)
elif len(sys.argv) >= 3:
  if str(sys.argv[2]) == "full":
    dall=1
  if str(sys.argv[2]) == "describe":
    dsall=1
  nsarg=str(sys.argv[1])
  podarg=str( sys.argv[2])
  if str(sys.argv[1]) == "nodes":
    if str(sys.argv[2]) != "":
      nall=1
      nsall=1
  if len(sys.argv) == 4:
    if str(sys.argv[3]) == "--image":
      dim=1
elif len(sys.argv) == 11:
  print("ty pidor")

if nall == 1:
  getPods = requests.get('https://kube-master01a.test.cognita.ru:6443/api/v1/nodes', verify='/var/lib/zabbix/scripts/pki/ca.crt', cert=('/var/lib/zabbix/scripts/pki/apiserver-kubelet-client.crt', '/var/lib/zabbix/scripts/pki/apiserver-kubelet-client.key'))
  data = json.loads(getPods.text)
  for i in data['items']:
#    print(i)
    for a in i['spec']:
      if str(a) == "externalID":
        host = str(i['spec'][a])
#      elif str(a) == "podCIDR":
      elif str(a) == "address":
        ip = str(i['spec'][a])
    for b in i['metadata']:
      if str(b) == "labels":
        for bb in i['metadata'][b]:
          if bb == "role":
            role = str(i['metadata'][b][bb])
    for c in i['status']:
      if str(c) == "conditions":
        for cc in i['status'][c]:
          if (cc['status'] == "True") and (str(cc['reason']) == "KubeletReady"):
            status=cc['type']
          else:
            status="False"
    if nsall !=1:
      print(host+": ("+ip+"), "+role+", "+status)
    else:
      if str(sys.argv[2]) == host:
        print(host+": ("+ip+"), "+role+", "+status)
else:
  getPods = requests.get('https://kube-master01a.test.cognita.ru:6443/api/v1/pods', verify='/var/lib/zabbix/scripts/pki/ca.crt', cert=('/var/lib/zabbix/scripts/pki/apiserver-kubelet-client.crt', '/var/lib/zabbix/scripts/pki/apiserver-kubelet-client.key'))
  data = json.loads(getPods.text)
  countd=0
  statusd=0
  statusrep="Not running is: "
  curver="none"
  vererr=""
  exist=0

  for i in data['items']:
    for a in i['metadata']:
      if a == "name":
        name = i['metadata'][a]
      if a == "namespace":
        namespace = i['metadata'][a]
    for b in i['spec']:
      if b == "nodeName":
        nodeName = i['spec'][b]
        for bb in i['spec']['containers']:
          image = bb['image']
    for c in i['status']:
      if c == "phase":
        phase = i['status'][c]
    for d in i['status']:
      if d == "startTime":
        startTime = i['status'][d]
#Для проверки битых подов!!!
#    if phase == "Failed":
#      print(namespace + " " + name + " " + phase)

#Какая-то старая хрень
#  if (namespace == "web") or (namespace == "hosting") or (namespace == "kube-system"):
#    date = datetime.now()
#    data_employee = (name, image, namespace, nodeName, startTime, phase, date)

#  if sall == 1:
#    print(data_employee)

#  else:
    if sall == 1:
      exist=exist+1
      countd=countd+1
      if phase == "Running":
        statusd=statusd+1
      else:
        statusrep=statusrep+" "+name
    else:
      if dall == 0:
        if dsall == 1 and (nsarg in namespace):
          print(namespace, nodeName, image, name, startTime, phase)
        else:
          gs=re.compile('^.*/(.*):')
          cname=gs.findall(image)
          if not cname:
            gs=re.compile('(.*):')
            cname=gs.findall(image)
            if not cname:
              cname=image
          if dim == 0:
            if (podarg in name) and (nsarg in namespace):
              exist=exist+1
              countd=countd+1
              gg=re.compile(':(.*)')
              ver=gg.findall(image)
              if curver == "none":
                curver=ver
              else:
                if (curver != ver):
                  vererr=str(vererr)+" // "+"Difference in versions detected: "+str(curver)+" and "+str(ver)
                  curver=ver
              if phase == "Running":
                statusd=statusd+1
              else:
                statusrep=statusrep+" "+name
          else:
            if (podarg in cname) and (nsarg in namespace):
              exist=exist+1
              countd=countd+1
              gg=re.compile(':(.*)')
              ver=gg.findall(image)
              if curver == "none":
                curver=ver
              else:
                if (curver != ver):
                  vererr=str(vererr)+" // "+"Difference in versions detected: "+str(curver)+" and "+str(ver)
                  curver=ver
              if phase == "Running":
                statusd=statusd+1
              else:
                statusrep=statusrep+" "+name
      else:
        exist=exist+1
        if (nsarg in namespace):
          countd=countd+1
          if phase == "Running":
            statusd=statusd+1
          else:
            statusrep=statusrep+" "+name

  if exist != 0 and dsall != 1:
    if dall != 1 and sall != 1 and dsall != 1:
      print("Pods running is: "+str(statusd)+"/"+str(countd)+"; with version: "+str(ver))
      if statusrep != "Not running is: ":
        print(statusrep)
      if vererr != 0:
        print(vererr)
    else:
      print("Pods running is: "+str(statusd)+"/"+str(countd))
      if statusrep != "Not running is: ":
        print(statusrep)
  elif dsall == 1:
    print("=)")
  else:
    print("No such pods or namespaces")

