from mpi4py import MPI
from datetime import datetime
import numpy
import hashlib

### define variables
pw = 'dunglt'
hashed_pw = hashlib.md5(pw).digest()
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
num_processes = comm.Get_size()
len_pw = len(pw)
characters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'n', 'm', 'o',
	      'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3',
	      '4', '5', '6', '7', '8', '9']
### dfs-root
def dfs_root(s, found, recv_req):
    ### stop dfs if a process has found true password
    for i in range(num_processes - 1):
        r = recv_req[i].test()
        if r[0] and (r[1] != None):
            print 3, ' recieved ', i
            return None, True
    ### compare current hashed pw with hashed pw
    if (len(s) == len_pw):
        #print s
        if (hashed_pw == hashlib.md5(s).digest()):
            return s, True
        else:
            return None, False
    ### add 1 more character to current str
    res = None
    for c in characters:
        s += c
        res, found = dfs_root(s, found, recv_req)
        s = s[:-1]
        if found:
            break
    return res, found

### dfs
def dfs(s, found, req):
    ### stop if root process send found pw message
    if req.Test():
        return None, True
    ### compare current hashed pw with hashed pw
    if (len(s) == len_pw):
        #print s
        if (hashed_pw == hashlib.md5(s).digest()):
            return s, True
        else:
            return None, False
    ### add 1 more character to current str
    for c in characters:
        s += c
        res, found = dfs(s, found, req)
        s = s[:-1]
        if found:
            break
    return res, found

### run on multi processes
def main():
    base = int(len(characters)/num_processes)
    ok = False
    found = False
    res = None
    print datetime.now()
    ### process root process
    if (rank == (num_processes - 1)):
        recv_req = []
        for i in range(num_processes - 1):
            recv_req.append(comm.irecv(source = i, tag = 2))
            print rank, ' wait recieve ', i
        while not found:
            for i in range(num_processes - 1):
                if recv_req[i].Test:
                    found = True
                    break
            if not ok:
                for c in characters[(num_processes - 1)*base:]:
                    res, found = dfs_root(c, found, recv_req)
                    if found:
                        break
                ok = True
        for i in range(num_processes - 1):
            send_req = comm.isend(True, dest = i, tag = 1)
            print rank, ' send ', i
        if (res != None):
            print res, ' ', rank

    ### process compute processes
    for i in range(0, num_processes - 1):
        if (rank == i):
            recv_req = comm.irecv(source = num_processes - 1, tag = 1)
            print rank, ' wait recieve'
            while not found:
                if recv_req.Test():
                    found = True
                    print rank, ' recieved'
                if not ok:
                    for c in characters[i*base:(i+1)*base]:
                        res, found = dfs(c, found, recv_req)
                        if found:
                            break
                    ok = True
                    send_req = comm.isend(res, dest = num_processes - 1, tag = 2)
                    print rank, ' send'
            if (res != None):
                print res, ' ', rank
    print datetime.now()

if __name__ == '__main__':
    main()
            
