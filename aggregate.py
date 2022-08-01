import errno
import json
import os
import shutil
import time
from os.path import dirname, abspath, isfile
import argparse

from git import Repo

parser = argparse.ArgumentParser(description='Aggregate all protobuf files')
parser.add_argument('coin', type=str, help="Coin to parse from the .json file in the config folder")
args = parser.parse_args()

# Get current directory
d = dirname(abspath(__file__))

# Check if requested coin has a config
coin = args.coin
try:
    config_path = os.path.join(d, f'configs/{coin.lower()}.json')
    f = open(config_path, "r")
    coin_config = json.load(f)
    f.close()
except Exception:
    print("Coin couldn't be found")
    exit()


tmp_dir = os.path.join(d, "tmp")
if not os.path.isdir(tmp_dir):
    os.mkdir(tmp_dir)

project_dir = os.path.join(tmp_dir, str(time.time()))
os.mkdir(project_dir)

# Delete all existing protobuf files
root_dir = 'src/cosmospy_protobuf'
root_abs_path = os.path.join(d, root_dir)
for filename in os.listdir(root_abs_path):
    file_path = os.path.join(root_abs_path, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (file_path, e))

# Load config
i = 1
for repo_url, repo_config in coin_config.items():
    print(f"Cloning {repo_url} | {repo_config['branch']}")
    repo_dir = project_dir + "/" + str(i)
    Repo.clone_from(
        repo_url,
        project_dir + "/" + str(i),
        branch=repo_config['branch']
    )

    # Copy proto files to root_dir
    for proto_folder in repo_config['paths']:
        proto_dir = os.path.join(repo_dir, proto_folder)
        category_name = proto_folder.split('/')[-1]
        try:
            shutil.copytree(proto_dir, root_abs_path + "/" + category_name, dirs_exist_ok=True, ignore=shutil.ignore_patterns("*.go"))
            print(f"Copied {category_name}")
        except OSError as exc:  # python >2.5
            try:
                shutil.copy(proto_dir, root_abs_path)
                print(f"File {proto_dir} copied successfully")
            except:
                raise

    i += 1




