#!/usr/bin/env python3
import os
import git
import sys
import json
import github
import shutil
import subprocess

from discord import Embed
from github import Github
from dotenv import load_dotenv
# from multiprocessing.pool import ThreadPool as Pool


load_dotenv()
gh = Github(os.getenv("GITHUB_TOKEN"))


async def scan_org(orgname, ctx=None):
    try:
        org = gh.get_organization(orgname)
    except Exception as e:
        # print("Organization not found.")
        await ctx.send(f"> Organization not found.")
        await ctx.send(e)
        return

    print(f"Scanning {orgname}")

    # Add /tmp when deploy
    workspace = f"{orgname}-workspace"
    if not os.path.exists(workspace):
        os.mkdir(f"{orgname}-workspace")

    # outputs = {}
    # pool = Pool(POOL_SIZE)

    for repo in list(org.get_repos()):
        # pool.apply_async(scan_worker, (workspace, orgname, repo, ctx,)).get()         
        print(f"Sending {repo}")
        await scan_worker(workspace, orgname, repo, ctx)


    # try:
    #     for repo in list(org.get_repos()):
    #         # pool.apply_async(scan_worker, (workspace, orgname, repo, ctx,)).get()         
    #         print(f"Sending {repo}")
    #         await scan_worker(workspace, orgname, repo, ctx)


    # except Exception as err:
    #     await ctx.send("> Something went wrong.")
    #     # return f"Bad Request: {err}", 400
    #     return

    # pool.close()
    # pool.join()

    print("Cleaning up")
    shutil.rmtree(workspace)
    return


async def scan_worker(workspace, orgname, repo, ctx=None):
    url = repo.clone_url
    name = repo.name
    
    # await ctx.send(f"> Scanning {orgname}/{repo.name}") 
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

        embed = Embed(title="Results", description="Hopefully some scan results:")
        for res in results["results"]:

            check_id = res["check_id"]
            path = res["path"]
            line_number = res["end"]["line"]

            url = f"https://github.com/{orgname}/{name}/blob/master/{path}#L{line_number}"

            embed.add_field(name="Vulnerability", value=check_id, inline=False)
            embed.add_field(name="URL", value=f"[Link]({url})")
            embed.add_field(name="Repository", value=name)
            embed.add_field(name="Path", value=path, inline=False)
            embed.add_field(name="Line Number", value=line_number, inline=False)
            
            await ctx.send(embed=embed)

        return
    else:
        await ctx.send(f"Nothing found :(")

    return