import socket
import asyncore
import select
import random
import pickle
import time
import json
import asyncio
import os
import sys
import threading
import math
import struct
from items import block_times
from subprocess import Popen
import hashlib, binascii, os
import zlib

def start2():
    BS = 10024
    outgoing = []
    active_players = {}
    arr = {}
    buffer = []
    buffert = []
    ids = {}
    conns = {}
    users = {}

    #Constants
    BIT = 0
    BYTE = 1
    STRING = 2
    INT = 3
    DOUBLE = 4
    FLOAT = 5
    SHORT = 6
    USHORT = 7

    #Send the packet
    def send(self, client):

        #Variables
        packet = client.packet
        types = ''.join(packet.BufferWriteT)
        length=struct.calcsize(types)

        #Send
        client.connection.send(struct.pack("="+types,*packet.BufferWrite))

    def hash_password(password):
        """Hash a password for storing."""
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
        pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                    salt, 100000)
        pwdhash = binascii.hexlify(pwdhash)
        return (salt + pwdhash).decode('ascii')

    def verify_password(stored_password, provided_password):
        """Verify a stored password against one provided by user"""
        salt = stored_password[:64]
        stored_password = stored_password[64:]
        pwdhash = hashlib.pbkdf2_hmac('sha512',
                                      provided_password.encode('utf-8'),
                                      salt.encode('ascii'),
                                      100000)
        pwdhash = binascii.hexlify(pwdhash).decode('ascii')
        return pwdhash == stored_password

    def readstring(mess):
        global mes
        s=""
        p=""
        while(p!="\x00"):
            p=struct.unpack('s', mess[:1])[0].decode("utf-8")
            mess=mess[1:]
            s+=p
        mes = mess
        return s[:-1]

    def readint(mess):
        global mes
        old = mess
        mes = mess[4:]
        return struct.unpack('i', old[:4])[0]

    def create_world(map):
        file = open(f"worlds/{map}.json", 'a')
        file.write("{}")
        file.close()
        file2 = open(f"worlds/{map}_seeds.json", 'a')
        file2.write("{}")
        file2.close()
        with open(f"worlds/{map}.json") as f:
            data = json.load(f)

        num = 0
        while num < 20:
            if num == 19:
                data[num] = ("0"*100)+"dd" + ("0"*98)
                num+=1
            else:
                data[num] = "0"*200
                num+=1
        while num < 25:
            if num == 20:
                data[num] = ("1"*100)+"bb" + ("1"*98)
                num+=1
            else:
                data[num] = "1"*200
                num+=1
        while num < 55:
            data[num] = "2"*200
            num+=1
        while num < 60:
            data[num] = "3"*200
            num+=1
        data[num] = "b"*200
        num+=1
        while num < 81:
            data[num] = "0"*200
            num+=1
        while num < 86:
            data[num] = "db"*100
            num+=1
        while num < 121:
            data[num] = "cb"*100
            num+=1

        with open(f"worlds/{map}.json", 'w+') as f:
            json.dump(data, f)


    class Packet():

        #Initialize the packet
        def __init__(self):

            #Buffer variables
            self.Buffer = -1
            self.BufferO = -1
            self.BufferWrite = []
            self.BufferWriteT = []


        #Clear the packet
        def clear(self):

            #Clear the lists
            self.BufferWrite.clear()
            self.BufferWriteT.clear()


        #Write to the packet
        def write(self, buffer_type, value):

            #Check for buffer type
            if buffer_type == BIT:
                self.BufferWrite.append(value)
                self.BufferWriteT.append("?")
            elif buffer_type == BYTE:
                self.BufferWrite.append(value)
                self.BufferWriteT.append("B")
            elif buffer_type == STRING:
                self.BufferWriteT.append("{}s".format(len(value)+1))
                self.BufferWrite.append(value.encode("utf-8")+b'\x00')
            elif buffer_type == INT:
                self.BufferWrite.append(value)
                self.BufferWriteT.append("i")
            elif buffer_type == DOUBLE:
                self.BufferWrite.append(float(value))
                self.BufferWriteT.append("d")
            elif buffer_type == FLOAT:
                self.BufferWrite.append(value)
                self.BufferWriteT.append("f")
            elif buffer_type == SHORT:
                self.BufferWrite.append(value)
                self.BufferWriteT.append("h")
            elif buffer_type == USHORT:
                self.BufferWrite.append(value)
                self.BufferWriteT.append("H")


        #Read from the packet
        def read(self, buffer_type):

            #Check for buffer type
            if buffer_type == BIT:
                Buffer2=self.Buffer
                self.Buffer=self.Buffer[1:]
                return struct.unpack('?', Buffer2[:1])[0]
            elif buffer_type == BYTE:
                Buffer2=self.Buffer
                self.Buffer=self.Buffer[1:]
                return struct.unpack('B', Buffer2[:1])[0]
            elif buffer_type == STRING:
                s=""
                p=""
                while(p!="\x00"):
                    p=struct.unpack('s', self.Buffer[:1])[0].decode("utf-8")
                    self.Buffer=self.Buffer[1:]
                    s+=p
                return s[:-1]
            elif buffer_type == INT:
                Buffer2=self.Buffer
                self.Buffer=self.Buffer[4:]
                return struct.unpack('i', Buffer2[:4])[0]
            elif buffer_type == DOUBLE:
                Buffer2=self.Buffer
                self.Buffer=self.Buffer[8:]
                return struct.unpack('d', Buffer2[:8])[0]
            elif buffer_type == FLOAT:
                Buffer2=self.Buffer
                self.Buffer=self.Buffer[4:]
                return struct.unpack('f', Buffer2[:4])[0]
            elif buffer_type == SHORT:
                Buffer2=self.Buffer
                self.Buffer=self.Buffer[2:]
                return struct.unpack('h', Buffer2[:2])[0]
            elif buffer_type == USHORT:
                Buffer2=self.Buffer
                self.Buffer=self.Buffer[2:]
                return struct.unpack('H', Buffer2[:2])[0]


        #Send the packet
        def send(self, client, pack, all = None):
            #Variables
            packet = pack
            types = ''.join(packet.BufferWriteT)
            length=struct.calcsize(types)
            if all == "all":
                for c in outgoing:
                    c.send(struct.pack("="+types,*packet.BufferWrite))
            else:
                #Send
                if client != None:
                    client.send(struct.pack("="+types,*packet.BufferWrite))

    def ping(self):
        lc = time.Time()

    class Minion:
      def __init__(self, ownerid, username, dir, map, level, shirt, pants):
        self.x = 50
        self.y = 50
        self.ownerid = ownerid
        self.username = username
        self.dir = dir
        self.map = map
        self.lc = time.time()
        self.lvl = level
        self.shirt = shirt
        self.pants = pants

    minionmap = {}
    chat = {}
    chat_player = {}

    def updateWorld(message):
      global mes
      mes = message
      packet = Packet()
      arr[0] = readstring(mes)

      if arr[0] == 'ping':
          id = readint(mes)
          minionmap[id].lc = time.time()

      if arr[0] == 'join world':
          playerid = readint(mes)
          username = readstring(mes)
          dir = readstring(mes)
          map = readstring(mes)
          check = os.path.isfile(f'./inventory/{username}.json')

          if check == False:
              lvl = 1
          else:
              with open(f"inventory/{username}.json") as f:
                  data = json.load(f)
              if "exp" in data:
                  lvl = math.trunc(data["exp"]/100)+1
              else:
                  lvl = 1
              print(lvl)
          playerminion = Minion(playerid, username, dir, map, lvl, "none", "none")
          minionmap[playerid] = playerminion
          check = os.path.isfile(f'./worlds/{map}.json')
          if check:
              with open(f"worlds/{map}.json") as f:
                  data = json.load(f)
              with open(f"ownership.json") as f:
                  owners = json.load(f)
              if map not in owners:
                owners[map] = "none";
              with open(f"ownership.json", 'w+') as f:
                  json.dump(owners, f)
              if len(data) > 50:
                  print(f"{username} has entered {map}")
                  remove = []
                  i = ids[playerid]
                  try:
                    for row in data:
                        packet.clear()
                        packet.write(2, "join")
                        packet.write(2, owners[map])
                        packet.write(3, playerid)
                        packet.write(2, data[row])
                        packet.send(i, packet)
                  except Exception:
                    remove.append(i)

      if arr[0] == 'create world':
          playerid = readint(mes)
          username = readstring(mes)
          dir = readstring(mes)
          map = readstring(mes)
          check = os.path.isfile(f'./worlds/{map}.json')
          print('world')

          if check == False:
              create_world(map)

      if arr[0] == "leave world":
          playerid = readint(mes)
          username = readstring(mes)
          world = readstring(mes)

          print(f"{username} has left {world}")

          minionmap.pop(playerid)

          remove = []

          for i in outgoing:
              try:
                  packet.clear()
                  packet.write(2, "leave")
                  packet.write(3, playerid)
                  packet.write(2, world)
                  packet.write(2, username)
                  packet.send(i, packet)
              except Exception:
                  remove.append(i)
                  continue

              for r in remove:
                  outgoing.remove(r)

      if arr[0] == 'time':
          if len(mes) > 3:
              world = readstring(mes)
              playerid = readint(mes)
              x = readint(mes)
              y = readint(mes)
              with open(f"worlds/{world}_seeds.json") as f:
                data = json.load(f)
              tim = int(data[str(y)+"_"+str(x)])-(math.trunc(time.time())-1570989351)
              if tim < 0:
                  tim = 0
              remove = []
              i = ids[playerid]
              try:
                    packet.clear()
                    packet.write(2, "time")
                    packet.write(3, tim)
                    packet.write(3, playerid)
                    packet.write(3, x)
                    packet.write(3, y)
                    packet.send(i, packet)
              except Exception:
                remove.append(i)

      if arr[0] == 'timecheck':
          if len(mes) > 3:
              world = readstring(mes)
              playerid = readint(mes)
              x = readint(mes)
              y = readint(mes)
              with open(f"worlds/{world}_seeds.json") as f:
                data = json.load(f)
              tim = int(data[str(y)+"_"+str(x)])-(math.trunc(time.time())-1570989351)
              if tim < 0:
                  tim = 0
              remove = []
              i = ids[playerid]
              print(tim)
              if tim == 0:
                  try:
                        packet.clear()
                        packet.write(2, "timecheck")
                        packet.write(3, tim)
                        packet.write(3, playerid)
                        packet.write(3, x)
                        packet.write(3, y)
                        packet.send(i, packet)
                  except Exception:
                    remove.append(i)

      if arr[0] == 'shopcheck':
          item = readstring(mes)
          amm = readint(mes)
          username = readstring(mes)
          cost = readint(mes)
          id = readint(mes)
          with open(f"inventory/{username}.json") as f:
            data = json.load(f)


          if data[str(50)] >= cost:
              i = ids[id]

              data[str(50)] = data[str(50)] - cost
              yy = 0
              while yy < 50:
                  if data[str(yy)] == str(item):
                      new_amount = int(data["num"+str(yy)])+ amm
                      data["num"+str(yy)] = new_amount
                      if new_amount <= 0:
                          data["num"+str(yy)] = -1
                          data[str(yy)] = "none"
                      yy = 100
                  elif data[str(yy)] == "none":
                      data[str(yy)] = item
                      data["num"+str(yy)] = 1
                      yy = 100
                  yy+=1
              with open(f"inventory/{username}.json", 'w+') as f:
                  json.dump(data, f)
              level = math.trunc(data["exp"]/100)+1
              with open(f"inventory/{username}.json") as f:
                data = json.load(f)
              remove = []
              send_items = {}
              send_amounts = {}

              xx = 0
              while xx < 50:
                  if xx == 0:
                      send_items = data[str(0)]
                      send_amounts = data["num"+str(xx)]
                      xx+=1
                  else:
                      send_items = send_items + "," + data[str(xx)]
                      send_amounts = str(send_amounts) + "," + str(data["num"+str(xx)])
                      xx+=1
              gems = data[str(50)]

              i = ids[id]
              try:
                packet.clear()
                packet.write(2, "inventory")
                packet.write(3, id)
                packet.write(2, send_items)
                packet.write(2, send_amounts)
                packet.write(3, level)
                packet.write(3, gems)
                packet.send(i, packet)
              except Exception:
                remove.append(i)

      if arr[0] == 'inventory update':
          username = readstring(mes)
          id = readint(mes)
          block = readstring(mes)
          amount = readint(mes)
          gem = readint(mes)

          with open(f"inventory/{username}.json") as f:
            data = json.load(f)

          yy = 0
          while yy < 50:
              if data[str(yy)] == str(block):
                  new_amount = int(data["num"+str(yy)])+ amount
                  data["num"+str(yy)] = new_amount
                  if new_amount <= 0:
                      x = yy
                      while x < 49:
                          data["num"+str(x)] = data["num"+str(x+1)]
                          data[str(x)] = data[str(x+1)]
                          x+=1
                  yy = 100
              elif data[str(yy)] == "none":
                  data[str(yy)] = block
                  data["num"+str(yy)] = 1
                  yy = 100
              yy+=1
          if "exp" not in data: data["exp"] = 0
          data[str(50)] = gem + data[str(50)]

          data["exp"] = data["exp"] + 1
          level = math.trunc(data["exp"]/100)+1

          with open(f"inventory/{username}.json", 'w+') as f:
              json.dump(data, f)

          with open(f"inventory/{username}.json") as f:
            data = json.load(f)
          remove = []
          send_items = {}
          send_amounts = {}

          xx = 0
          while xx < 50:
              if xx == 0:
                  send_items = data[str(0)]
                  send_amounts = data["num"+str(xx)]
                  xx+=1
              else:
                  send_items = send_items + "," + data[str(xx)]
                  send_amounts = str(send_amounts) + "," + str(data["num"+str(xx)])
                  xx+=1
          gems = data[str(50)]

          i = ids[id]
          try:
            packet.clear()
            packet.write(2, "inventory")
            packet.write(3, id)
            packet.write(2, send_items)
            packet.write(2, send_amounts)
            packet.write(3, level)
            packet.write(3, gems)
            packet.send(i, packet)
          except Exception:
            remove.append(i)


      if arr[0] == 'inventory':
          print("inventory")
          username = readstring(mes)
          id = readint(mes)

          check = os.path.isfile(f'./inventory/{username}.json')

          if check == False:
              file = open(f"inventory/{username}.json", 'a')
              file.write("{}")
              file.close()

              data = {}
              numb = {}
              data[0] = "breaker"
              data['num0'] = 1
              numb[0] = 1
              data[1] = "wrench"
              data['num1'] = 1
              numb[1] = 1
              xx = 2
              while xx < 50:
                  data[xx] = "none"
                  data["num"+str(xx)] = -1
                  numb[xx] = -1
                  xx+=1
              data[50] = 0

              with open(f"inventory/{username}.json", 'w+') as f:
                  json.dump(data, f)

          with open(f"inventory/{username}.json") as f:
            data = json.load(f)
          if "exp" not in data:
              data["exp"] = 0
          level = math.trunc(data["exp"]/100)+1

          remove = []
          send_items = {}
          send_amounts = {}

          xx = 0
          while xx < 50:
              if xx == 0:
                  send_items = data[str(0)]
                  send_amounts = data["num"+str(xx)]
                  xx+=1
              else:
                  send_items = send_items + "," + data[str(xx)]
                  send_amounts = str(send_amounts) + "," + str(data["num"+str(xx)])
                  xx+=1
          gems = data[str(50)]

          i = ids[id]
          try:
                packet.clear()
                packet.write(2, "inventory")
                packet.write(3, id)
                packet.write(2, send_items)
                packet.write(2, send_amounts)
                packet.write(3, level)
                packet.write(3, gems)
                packet.send(i, packet)
          except Exception:
                remove.append(i)


      if arr[0] == 'position update':
          playerid = readint(mes)
          x = readint(mes)
          y = readint(mes)
          dir = readstring(mes)
          world = readstring(mes)
          shirt = readstring(mes)
          pants = readstring(mes)

          if playerid == 0: return

          minionmap[playerid].x = x
          minionmap[playerid].y = y
          minionmap[playerid].dir = dir
          minionmap[playerid].shirt = shirt
          minionmap[playerid].pants = pants

          remove = []

          for i in outgoing:
            try:
                num = 0
                for key, value in minionmap.items():
                  if value.ownerid != playerid:
                          packet.clear()
                          packet.write(2, "position update")
                          packet.write(3, value.ownerid)
                          packet.write(3, value.x)
                          packet.write(3, value.y)
                          packet.write(2, value.username)
                          packet.write(2, value.dir)
                          packet.write(2, value.map)
                          packet.write(3, value.lvl)
                          packet.write(2, value.shirt)
                          packet.write(2, value.pants)
                          packet.send(i, packet)
            except Exception:
                remove.append(i)
                continue


            for r in remove:
                outgoing.remove(r)
      if arr[0] == 'register':
            username = readstring(mes)
            password = hash_password(readstring(mes))
            id = readint(mes)
            with open("users.json") as f:
                data = json.load(f)
            if username not in data:
                data[username] = password
                print(f"{username} has registed")
            with open("users.json", 'w+') as f:
                json.dump(data, f)
            remove = []
            i = ids[id]
            try:
                packet.clear()
                packet.write(2, 'register')
                packet.write(2, "success")
                packet.send(i, packet)
            except Exception:
                remove.append(i)


      if arr[0] == 'login':
            vers = readint(mes)
            username = readstring(mes)
            password = readstring(mes)
            id = readint(mes)
            with open("users.json") as f:
                data = json.load(f)
            #with open("discord.json") as f:
            #    disc = json.load(f)
            #if "online" not in disc:
            #    disc["online"] = 0
            if username in data:
                if verify_password(data[username], password):
                    print(vers)
                    if vers == 6:
                        print(active_players)
                        if username not in active_players:
                        #    disc["online"]+=1
                            users[id] = username
                            active_players[username] = True
                            print(f"{username} has logined")
                            remove = []

                            update = ['login data', "success"]
                            i = ids[id]
                            try:
                                packet.clear()
                                packet.write(2, 'login')
                                packet.write(2, "success")
                                packet.write(3, id)
                                packet.send(i, packet)
                            except Exception:
                                remove.append(i)
                        else:
                            print("Played already logined")
                with open("users.json", 'w+') as f:
                    json.dump(data, f)
            #    with open("discord.json", 'w+') as f:
            #        json.dump(disc, f)

      if arr[0] == "chat":
          player = readstring(mes)
          message = readstring(mes)
          print(player + ":" + message)
          remove = []
          for i in outgoing:
              try:
                  packet.clear()
                  packet.write(2, "chat")
                  packet.write(2, player)
                  packet.write(2, message)
                  packet.send(i, packet)
              except Exception:
                  remove.append(i)
                  continue

              for r in remove:
                  outgoing.remove(r)

      if arr[0] == "access":
          pid = readint(mes)
          map = readstring(mes)
          user = readstring(mes)
          with open(f"ownership.json") as f:
              owner = json.load(f)
          if owner[map] == user or owner[map] == "none":
              remove = []
              i = ids[pid]
              try:
                print("W")
                packet.clear()
                packet.write(2, "access")
                packet.send(i, packet)
              except Exception:
                remove.append(i)

      if arr[0] == "map update":
          pid = readint(mes)
          x = readint(mes)*2+2
          y = readint(mes)
          bt = readstring(mes)
          type = readstring(mes)
          world = readstring(mes)
          username = readstring(mes)
          if bt == "b":
              y += 61
          if type == "create":
              block = readstring(mes)
              id = readstring(mes)
              blk = "-1"
          else:
              blk = readstring(mes)
              block = "00"
          print("MAP UPDATE:" + world)

          with open(f"ownership.json") as f:
              owner = json.load(f)

          with open(f"worlds/{world}.json") as f:
              data = json.load(f)

          with open(f"worlds/{world}_seeds.json") as f:
              seeds = json.load(f)
          print(world)
          if owner[world] == "none" or owner[world] == username:
              if "seed" in block:
                  val = time.time()
                  date = math.trunc(val)-1570989351
                  newx = math.trunc(x/2-1)
                  newblock = block.replace("tree", "")
                  totaltime = date + block_times(newblock)
                  seeds[str(y) + "_" + str(newx)] = totaltime
              row = data[str(y)]


              if type == "create":
                  if block == "wl":
                      owner[world] = username;
                  row2 = row[:x-2] + id + row[x:]
              else:
                  row2 = row[:x-2] + block + row[x:]
              if blk == "wl":
                  owner[world] = "none"

              data[str(y)] = row2
              with open(f"ownership.json", 'w+') as f:
                  json.dump(owner, f)
              with open(f"worlds/{world}.json", 'w+') as f:
                json.dump(data, f)
              with open(f"worlds/{world}_seeds.json", 'w+') as f:
                json.dump(seeds, f)
              remove = []
              print(x)
              print(y)
              if bt == "b":
                  y-=61
              for i in outgoing:
                  try:
                      packet.clear()
                      packet.write(2, "mapupdate")
                      packet.write(3, pid)
                      packet.write(3, x)
                      packet.write(3, y)
                      packet.write(2, world)
                      packet.write(2, type)
                      packet.write(2, block)
                      packet.write(2, blk)

                      packet.send(i, packet)
                  except Exception:
                      remove.append(i)
                      continue

                  for r in remove:
                      outgoing.remove(r)
      if arr[0] == "ban":
          user = readstring(mes)

      if arr[0] == "give":
          id = readint(mes)
          user = readstring(mes)
          item = readstring(mes)
          count = readint(mes)
          with open('admins.json') as f:
              admins = json.load(f)
          if user in admins:
              remove = []
              i = ids[id]
              try:
                packet.clear()
                packet.write(2, "give")
                packet.write(2, user)
                packet.write(2, item)
                packet.write(3, count)
                packet.send(i, packet)
              except Exception:
                remove.append(i)


      if arr[0] == "friends":
          id = readint(mes)
          username = readstring(mes)
          check = os.path.isfile(f'./friends/{username}.json')
          if check == False:
              file = open(f"friends/{username}.json", 'a')
              file.write("{}")
              file.close()
          with open(f'./friends/{username}.json') as f:
              f1 = json.load(f)
          remove = []
          i = ids[id]
          try:
            packet.clear()
            packet.write(2, "friends")
            packet.write(3, len(f1))
            for e in f1:
                l = f1[e]
                if l in active_players:
                    packet.write(2, l)
                    packet.write(3, 0)
                else:
                    packet.write(2, l)
                    packet.write(3, 1)
            packet.send(i, packet)
          except Exception:
            remove.append(i)

      if arr[0] == "friendadd":
          username = readstring(mes)
          pid = readint(mes)
          friend = readstring(mes)
          check = os.path.isfile(f'./friends/{username}.json')

          if check == False:
              file = open(f"friends/{username}.json", 'a')
              file.write("{}")
              file.close()

          for i in outgoing:
              try:
                packet.clear()
                packet.write(2, "frequest")
                packet.write(2, username)
                packet.write(2, friend)
                packet.send(i, packet)
              except Exception:
                remove.append(i)
                continue

                for r in remove:
                  outgoing.remove(r)
      if arr[0] == "accept":
          username = readstring(mes)
          username2 = readstring(mes)
          check = os.path.isfile(f'./friends/{username}.json')
          if check == False:
              file = open(f"friends/{username}.json", 'a')
              file.write("{}")
              file.close()
          with open(f'./friends/{username}.json') as f:
              f1 = json.load(f)
          with open(f'./friends/{username2}.json') as f:
              f2 = json.load(f)
          f1[len(f1)+1] = username2
          f2[len(f2)+1] = username
          with open(f'./friends/{username}.json', 'w+') as f:
            json.dump(f1, f)
          with open(f'./friends/{username2}.json', 'w+') as f:
            json.dump(f2, f)

      if arr[0] == "disconnect":
            player_id = readint(mes)
            username = readstring(mes)
            remove = []
            for i in outgoing:
                  try:
                      packet.clear()
                      packet.write(2, "disconnect")
                      packet.write(3, player_id)
                      packet.write(2, username)
                      packet.send(i, packet)
                  except Exception:
                      remove.append(i)
                      continue

                  for r in remove:
                      outgoing.remove(r)

      if packet.Buffer > 0:
          updateWorld(mes)

    class MainServer(asyncore.dispatcher):
      def __init__(self, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(('192.241.135.129', port))  #192.241.135.129
        self.listen(10)
        print("Server is up")
      def handle_accept(self):
        conn, addr = self.accept()
        print ('Connection address:' + addr[0] + " " + str(addr[1]))
        conn.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
        outgoing.append(conn)
        playerid = len(ids)+1
        conns[conn] = playerid
        update = ['id update', playerid]
        ids[playerid] = conn
        packet = Packet()
        packet.clear()
        packet.write(2, 'id update')
        packet.write(3, playerid)
        packet.send(conn, packet)
        num = 0
        while num < 5:
            chat[num] = None
            chat_player[num] =None
            num+=1
        Run(conn, playerid)

    class Run(asyncore.dispatcher_with_send):
      def __init__(self, cd, pi):
          self.pi = pi
          threading.Thread.__init__(self)
          asyncore.dispatcher_with_send.__init__(self, cd)

      def handle_read(self):
        recievedData = self.recv(BS)
        if recievedData:
          updateWorld(recievedData)
        else:
            player_id = self.pi
            packet = Packet()
        #    with open("discord.json") as f:
        #        disc = json.load(f)
            #disc["online"]-=1
            #with open("discord.json", 'w+') as f:
             #  json.dump(disc, f)
            if player_id in users:
                username = users[player_id]
                print(f"{users[player_id]} has disconnected")
                active_players.pop(users[player_id])
                users.pop(player_id)
                outgoing.remove(ids[player_id])
            if player_id in minionmap:
                minionmap.pop(player_id)

            self.close()


    MainServer(4322)
    asyncore.loop()
start2()
