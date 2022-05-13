#!/usr/bin/env python3
import os
import json
import base64
import shutil
import logging
import requests
import subprocess

from flask import Flask, request

#from concurrent.futures import ProcessPoolExecutor as Pool
#from multiprocessing import Pool
from multiprocessing.pool import ThreadPool as Pool

import git
import github
from github import Github

POOL_SIZE = 10

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = Flask(__name__)
gh = Github(os.getenv("GITHUB_TOKEN"))

DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")


@app.route("/", methods=["POST"])
def handler():
    envelope = request.get_json()
    if not envelope:
        msg = "no Pub/Sub message received"
        return f"Bad Request: {msg}", 400
    if not isinstance(envelope, dict) or "message" not in envelope:
        msg = "invalid Pub/Sub message format"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    # decode the message payload and recover metadata
    data = envelope["message"]["data"]
    payload = base64.b64decode(data).decode("utf-8")
    payload = json.loads(payload)
    orgname = payload["orgname"]

    try:
        org = gh.get_organization(orgname)
    except github.GithubException.UnknownObjectException:
        print("Organization not found.")
        return f"Bad Request: {msg}", 400

    print(f"Scanning {orgname}")

    workspace = f"{orgname}-workspace"
    if not os.path.exists(workspace):
        os.mkdir(f"{orgname}-workspace")

    outputs = {}
    pool = Pool(POOL_SIZE)
    try:
        for repo in list(org.get_repos()):
            results = pool.apply_async(scan_worker, (workspace, orgname, repo,)).get()
            #results = scan_worker(workspace, orgname, repo)
            if results:
                outputs[repo.full_name] = results

    except Exception as err:
        return f"Bad Request: {err}", 400

    pool.close()
    pool.join()

    if len(outputs) != 0:
        with open(f"{orgname}-results.json", "w") as fd:
            fd.write(json.dumps(outputs, indent=4))
        print(outputs)
    else:
        print("Nothing found :(")

    print("Cleaning up")
    shutil.rmtree(workspace)
    return ("", 204)


def scan_worker(workspace, orgname, repo):
    url = repo.clone_url
    name = repo.name
    
    print(f"{orgname}/{name}")

    # clone repo if not exists
    repo_workspace = os.path.join(workspace, name)
    if not os.path.exists(repo_workspace):
        repo = git.Repo.clone_from(url, os.path.join(workspace, name))

    # look for CI/CD configs
    workflow_path = os.path.join(repo_workspace, ".github")
    if not os.path.exists(workflow_path):
        #print("No workflows to scan")
        return
    
    # run semgrep and parse the detection and path
    res = subprocess.run(["semgrep", "--json", "--config", "rules", workflow_path], capture_output=True)
    results = json.loads(res.stdout.decode("utf-8"))
    shutil.rmtree(repo_workspace)

    if len(results["results"]) != 0:
        finalized = {}
        for res in results["results"]:
            finalized[res["check_id"]] = res["path"]

        print(name, finalized)
        requests.post(
        return finalized

    return None

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
