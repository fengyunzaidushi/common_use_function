import requests
from collections import defaultdict
from dotenv import load_dotenv
import os,json

# 加载 .env 文件
load_dotenv()

# 现在你可以像平常一样使用 os.environ 获取环境变量
oauth_token = os.environ.get('GITHUB_OAUTH_TOKEN')
if oauth_token is None:
    print("环境变量 GITHUB_OAUTH_TOKEN 未设置")
else:
    headers = {'Authorization': f'token {oauth_token}'}


def get_file_commit_times(repo_user, repo_name, path=""):
    api_url = f"https://api.github.com/repos/{repo_user}/{repo_name}/commits"
    params = {'path': path}
    commits = requests.get(api_url, params=params, headers=headers).json()  # 添加 headers 参数

    if "message" in commits:
        print(f"Error: {commits['message']}")
        return []

    return [commit['commit']['author']['date'] for commit in commits]

if not os.path.exists('history'):
    os.makedirs('history')
def get_files_by_commit_date(file_commit_times):
    date_to_files = defaultdict(list)
    for file_path, commit_times in file_commit_times.items():
        for commit_time in commit_times:
            date_to_files[commit_time].append(file_path)
    return date_to_files
if __name__ == "__main__":
    # repo_user = input("请输入GitHub仓库的用户名：")
    # repo_name = input("请输入GitHub仓库的名称：")
    repo_directory = "https://github.com/fengyunzaidushi/common_use_function.git"
    master = ['main','master'][0]
    repo_list = repo_directory.strip('.git').strip('https://').split('/')
    repo_user = repo_list[1]
    repo_name = repo_list[2]
    # 获取仓库的文件列表，这里只演示了根目录，实际应用可能需要递归获取所有目录和文件
    api_url = f"https://api.github.com/repos/{repo_user}/{repo_name}/git/trees/{master}?recursive=1"
    tree = requests.get(api_url, headers=headers).json()

    if "tree" not in tree:
        print(f"Error: {tree.get('message', 'Unknown error')}")
        exit(1)

    file_commit_times = defaultdict(list)
    prefix = repo_directory.strip('.git') + '/blob/' + master + '/'
    for entry in tree['tree']:
        if entry['type'] == 'blob':  # 只处理文件，不处理目录
            print(f"正在处理：{entry['path']} ...")
            commit_times = get_file_commit_times(repo_user, repo_name, entry['path'])
            if commit_times:
                file_commit_times[prefix+entry['path']] = commit_times

    # 按照最近提交时间排序文件
    sorted_files = sorted(file_commit_times.items(), key=lambda x: x[1][0], reverse=True)

    output_file = os.path.join(f'history', f'{repo_user}_{repo_name}_提交历史-文件.py')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('"""' + '\n')
        json.dump(dict(sorted_files), f, ensure_ascii=False, indent=4)
        f.write('"""' + '\n')


    # 按日期组织文件
    date_to_files = get_files_by_commit_date(file_commit_times)
    # 按照提交时间排序文件
    sorted_files = sorted(date_to_files.items(), key=lambda x: x[0], reverse=True)

    output_file = os.path.join(f'history', f'{repo_user}_{repo_name}_提交历史-时间.py')
    # 写入到json文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('"""' + '\n')
        json.dump(dict(sorted_files), f, ensure_ascii=False, indent=4)
        f.write('"""' + '\n')
