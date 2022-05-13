#!/usr/bin/env python3
import sys
import os
import json
import shutil
import subprocess
import dotenv
dotenv.load_dotenv()

#from concurrent.futures import ProcessPoolExecutor as Pool
#from multiprocessing import Pool
from multiprocessing.pool import ThreadPool as Pool

import git
import github
from github import Github

POOL_SIZE = 10
TOKEN = os.getenv("GITHUB_TOKEN")

def scan_worker(workspace, orgname, repo):
    url = repo.clone_url
    name = repo.name
    
    print(f"{orgname}/{name}")

    # clone repo if not exists
    repo_workspace = os.path.join(workspace, name)
    if not os.path.exists(repo_workspace):
        repo = git.Repo.clone_from(url, os.path.join(workspace, name))

    # look for CI/CD configs
    targets = [".github", ".circleci", ".azure-pipelines", ".ci"]
    found = False
    for t in targets:
        workflow_path = os.path.join(repo_workspace, t)
        if os.path.exists(workflow_path):
            found = True
            break

    if not found:
        return
    
    # run semgrep and parse the detection and path
    res = subprocess.run(["semgrep", "--json", "--config", "rules", repo_workspace], capture_output=True)
    results = json.loads(res.stdout.decode("utf-8"))
    shutil.rmtree(repo_workspace)

    if len(results["results"]) != 0:
        finalized = {}
        for res in results["results"]:
            finalized[res["check_id"]] = res["path"]

        print(name, finalized)
        return finalized

    return None

def main():
    gh = Github(TOKEN)

    for project in os.listdir("projects"):
        conf = os.path.join("projects", project)
        with open(conf) as fd:
            content = json.loads(fd.read())

        if not "social" in content:
            continue
        if not "github" in content["social"]:
            continue

        orgname = content["social"]["github"]
        try:
            org = gh.get_organization(orgname)
        except Exception as err:
            print(err)
            continue

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
            print(err)
            print("Interrupted, exiting early...")
            break

        pool.close()
        pool.join()

        if len(outputs) != 0:
            with open(f"results/{orgname}-results.json", "w") as fd:
                fd.write(json.dumps(outputs, indent=4))
            print(outputs)
        else:
            print("Nothing found :(")

        print("Cleaning up")
        os.remove(conf)
        shutil.rmtree(workspace)

if __name__ == "__main__":
    main()
