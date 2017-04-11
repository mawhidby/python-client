#!/usr/bin/env python

import tempfile
import random
import string
import requests
import re
import sys
import os
import time
import subprocess
from contextlib import contextmanager

ACCOUNT_ID_MATCHER = re.compile("Account ID: (.+)")
ACCOUNT_SECRET_MATCHER = re.compile("Account secret: (.+)")

@contextmanager
def server(env):
    """
    Context manager for running the server. This starts the server up, waits
    until its responsive, then yields. When the context manager's execution is
    resumed, it kills the server.
    """

    # Start the process
    server_proc = subprocess.Popen(["braid-server"], stdout=sys.stdout, stderr=sys.stderr, env=env)
    
    while True:
        # Check if the server is now responding to HTTP requests
        try:
            res = requests.get("http://localhost:8000", timeout=1)

            if res.status_code == 401:
                break
        except requests.exceptions.RequestException:
            pass

        # Server is not yet responding to HTTP requests - let's make sure it's
        # running in the first place
        if server_proc.poll() != None:
            raise Exception("Server failed to start")

        time.sleep(1)

    try:
        yield
    finally:
        server_proc.terminate()

def create_account(env):
    """Creates a braid account"""
    random_value = "".join(random.sample(string.ascii_letters + string.digits, 10))
    email = "%s@braidery.github.io" % random_value
    create_user_proc = subprocess.Popen(["braid-user", "add", email], env=env, stdout=subprocess.PIPE, stderr=sys.stderr)
    create_user_output, _ = create_user_proc.communicate()
    create_user_output_str = create_user_output.decode("utf-8")
    account_id = ACCOUNT_ID_MATCHER.search(create_user_output_str).groups()[0]
    secret = ACCOUNT_SECRET_MATCHER.search(create_user_output_str).groups()[0]
    return account_id, secret

def main():
    with tempfile.TemporaryDirectory(prefix="braid-python-client") as rdb_dir:
        env = dict(os.environ)

        env.update({
            "RUST_BACKTRACE": "1",
            "DATABASE_URL": "rocksdb://%s" % rdb_dir,
            "BRAID_SCRIPT_ROOT": "%s/test_scripts" % os.getcwd(),
            "BRAID_HOST": "localhost:8000",
        })

        account_id, secret = create_account(env)

        with server(env):
            env.update({
                "BRAID_ACCOUNT_ID": account_id,
                "BRAID_SECRET": secret,
            })

            proc = subprocess.Popen(
                ["nosetests", "braid.test"],
                stdout=sys.stdout,
                stderr=sys.stderr,
                env=env
            )

            rc = proc.wait()
            sys.exit(rc)

if __name__ == "__main__":
    main()
