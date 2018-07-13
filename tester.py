#!/usr/bin/python3
'''
This script finds corner cases of your program by testing it against a correct solution. The script uses Stress Testing to find the corner cases. Currently, the script checks program written in java only.

'''

import argparse
import requests
import os
import subprocess
from bs4 import BeautifulSoup


class InvalidFilePath(Exception):
    pass


class ConnectionError(Exception):
    pass


class ExecutionError(Exception):
    pass


class SolutionParsing(Exception):
    pass


def getfilename(source):
    # to be implemeted using regex for better matching
    index = source.find('public class')
    if(index == -1):
        raise SolutionParsing('error while parsing solution')
    index1 = source.find('{', index)
    if(index1 == -1):
        raise SolutionParsing('error while parsing solution')
    name = source[index + 12:index1].strip()
    return name


def filepath(path):
    if not path.endswith('.java'):
        raise InvalidFilePath('the path should point to a java file')
    if path.startswith('/home/romit17'):
        return path
    if path[0].startswith('./'):
        path = path[1:]
    else:
        path = '/' + path
    return os.getcwd() + path


def filepathorid(args):
    if not args.contestID:
        return filepath(args.sol)
    url = 'http://codeforces.com/contest/' + \
        args.contestID + '/submission/' + args.sol
    r = requests.get(url)
    attempt = 1
    while r.status_code != 200:
        r = requests.get(url, allow_redirects=False)
        attempt += 1
        if attempt > 5:
            raise ConnectionError(
                'error connecting codeforces server, response returned with status', r.status_code)
    source = BeautifulSoup(
        r.text, 'html.parser').pre.contents[0].replace('\r\n', '\n')
    #source = source.replace('public class', 'class', 1)
    fname = getfilename(source)
    fname += '.java'
    with open(fname, 'w') as f:
        f.write(source)
    return os.getcwd() + '/' + fname


def getcodefile(args):
    tcase = filepath(args.tcase)
    code = filepath(args.code)
    sol = filepathorid(args)
    return tcase, code, sol


def compiling(*arg):
    javapath = '/home/romit17/Desktop/'
    for prg in arg:
        proc = subprocess.run(
            ['javac', '-d', javapath, prg], stderr=subprocess.STDOUT)
        proc.check_returncode()
        print(proc.args)


def execute(path, inp=None):
    javapath = '/home/romit17/Desktop'
    path = path.split('/')[-1].split('.')[0]
    proc = subprocess.run(['java', '-cp', javapath, path], stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, input=inp, universal_newlines=True)
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr)
        raise ExecutionError(
            'runtime error {} occured for path: {}'.format(proc.returncode, path))
    return proc.stdout


def testing(*arg):
    try:
        count = 0
        while (not arg[3]) or count < arg[3]:
            count += 1
            inp = execute(arg[0])
            out1 = execute(arg[1], inp)
            out2 = execute(arg[2], inp)
            if(out1 == out2):
                print('Test Case#', count, '   ok', end='\r')
            else:
                print('output mismatch')
                print('\ninput:')
                print(inp)
                print('\noutput1(code):')
                print(out1)
                print('\noutput2(solution):')
                print(out2)
                return
    except KeyboardInterrupt:
        print('KeyboardInterrupt given')
        print('Number of tests executed', count)
        return


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        'tcase', help='absolute or relative path to test case generator java program')
    parser.add_argument(
        'code', help='abosulute or relative path to java source code to test')
    parser.add_argument(
        'sol', help='codeforces submission id or absolute or relative path to correct java code to test against')
    parser.add_argument(
        '-c', '--contestID', help='contest id of codeforces solution; to be provided when submission id is provided in sol argument else not')
    parser.add_argument(
        '-t', '--times', help='number of times to test source code against solution code; infinity if not provided')
    args = parser.parse_args()
    tcase, code, sol = getcodefile(args)
    # print(tcase,code,sol)
    print('compiling files....')
    compiling(tcase, code, sol)
    print('compiling done')
    print('starting Stress Testing')
    testing(tcase, code, sol, args.times)


if __name__ == '__main__':
    main()
