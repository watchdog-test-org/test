import os
import sys
import hashlib

keys = {}
root = "./data/keys/"
usernames = os.listdir(root)

os.makedirs("api/names/")
for username in usernames:
    f = open(root + username, "r")
    sshkey = f.read()
    sshkey = sshkey.split(' ')[0] + " " + sshkey.split(' ')[1]
    keys[username] = hashlib.sha256(sshkey.encode()).hexdigest()
    f = open("api/names/{}".format(keys[username]), "w")
    f.write(username)
    f.close()


def make_route(host, ruser, keyhash):
    if os.path.exists("api/access/{}/{}".format(host, ruser)) == False:
        os.makedirs("api/access/{}/{}".format(host, ruser))
    f = open("api/access/{}/{}/{}".format(host, ruser, keyhash), "w")
    f.write("1")
    f.close()


for username in os.listdir("data/hosts"):
    fp = open("data/hosts/{}".format(username))
    lines = fp.readlines()
    for l in lines:
        if l == '\n':
            continue
        l = l.strip()
        idx = l.index('|')
        hostname = l[:idx]
        ruser = l[idx+1:]
        keyhash = keys[username]
        make_route(hostname, ruser, keyhash)