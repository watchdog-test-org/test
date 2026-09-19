import os
import sys
import hashlib
import json
import string

ALLOWED = string.ascii_lowercase + string.digits + "-"

valid = True

keys = {}
root = "./data/keys/"
usernames = os.listdir(root)

os.makedirs("api/names/", exist_ok=True)
for username in usernames:
    filename = root + username

    if username[0] not in string.ascii_lowercase:
        print("Invalid username \"{}\" in key file \"{}\": must start with a lowercase letter".format(username, filename), file=sys.stderr)
        valid = False
        continue

    bad = [c for c in username if c not in ALLOWED]
    if bad:
        print("Invalid username \"{}\" in key file \"{}\": contains invalid character {!r} (only letters, digits and '-' allowed)".format(username, filename, bad[0]), file=sys.stderr)
        valid = False
        continue

    f = open(filename, "r")
    parts = f.read().split()
    f.close()
    if len(parts) < 2:
        print("Key file \"{}\" does not look like an SSH public key".format(filename), file=sys.stderr)
        valid = False
        continue

    sshkey = parts[0] + " " + parts[1]
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


def load_json():
    f = open("config.json")
    config = json.load(f)
    f.close()
    return config


config = load_json()

hosts = config["hosts"]
for username in os.listdir("data/hosts"):
    filename = "data/hosts/{}".format(username)

    if username not in keys:
        print("Hosts file \"{}\" has no matching valid key".format(filename), file=sys.stderr)
        valid = False
        continue

    fp = open(filename)
    lines = fp.readlines()
    fp.close()
    for l in lines:
        if l == '\n':
            continue
        l = l.strip()

        if "|" not in l:
            print("Entry \"{}\" in file \"{}\" does not contain \"|\"".format(l, filename), file=sys.stderr)
            valid = False
            continue

        idx = l.index('|')
        hostname = l[:idx]
        ruser = l[idx + 1:]

        if len(hostname) == 0:
            print("Empty hostname in file \"{}\"".format(filename), file=sys.stderr)
            valid = False
            continue
        if hostname not in hosts:
            print("Invalid hostname \"{}\" in file \"{}\"".format(hostname, filename), file=sys.stderr)
            valid = False
            continue

        if len(ruser) == 0:
            print("Empty remote username in file \"{}\"".format(filename), file=sys.stderr)
            valid = False
            continue

        if ruser[0] not in string.ascii_lowercase:
            print("Invalid remote username \"{}\" in file \"{}\": must start with a letter".format(ruser, filename), file=sys.stderr)
            valid = False
            continue

        bad = [c for c in ruser if c not in ALLOWED]
        if bad:
            print("Invalid remote username \"{}\" in file \"{}\": contains invalid character {!r} (only letters, digits and '-' allowed)".format(ruser, filename, bad[0]), file=sys.stderr)
            valid = False
            continue

        keyhash = keys[username]
        make_route(hostname, ruser, keyhash)

if not valid:
    sys.exit(1)
