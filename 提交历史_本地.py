import os
import subprocess
from collections import defaultdict
import json

def get_all_files(directory='.'):
    for foldername, _, filenames in os.walk(directory):
        for filename in filenames:
            yield os.path.join(foldername, filename)


def get_file_commit_times(repo_directory, file_path):
    try:
        log = subprocess.check_output(
            ['git', '-C', repo_directory, 'log', '--pretty=format:%cd', '--date=short', '--', file_path],
            stderr=subprocess.DEVNULL).decode("utf-8")
        if log:
            return log.split('\n')
        else:
            return []
    except subprocess.CalledProcessError:
        return []
def get_files_by_commit_date(file_commit_times):
    date_to_files = defaultdict(list)
    for file_path, commit_times in file_commit_times.items():
        for commit_time in commit_times:
            date_to_files[commit_time].append(file_path)
    return date_to_files

if __name__ == '__main__':
    # repo_directory = input("请输入Git仓库的目录路径：")  # 从用户那里获取Git仓库的路径
    repo_directory = '/mnt/sda/github/10yue/openai-cookbook'
    master = ['main', 'master'][0]
    origin_repo_dir = 'https://github.com/openai/openai-cookbook.git'
    prefix = origin_repo_dir.strip('.git') + '/blob/' + master + '/'
    file_commit_times = defaultdict(list)

    for file_path in get_all_files(repo_directory):
        rel_file_path = os.path.relpath(file_path, start=repo_directory)  # 获取相对于仓库根目录的文件路径
        commit_times = get_file_commit_times(repo_directory, rel_file_path)
        if commit_times:
            file_commit_times[prefix+rel_file_path] = commit_times

    # 按照最近提交时间排序文件
    sorted_files = sorted(file_commit_times.items(), key=lambda x: x[1][0], reverse=True)
    if not os.path.exists(repo_directory+'/history'):
        os.makedirs(repo_directory+'/history')
    output_file = os.path.join(repo_directory+'/history', '本地提交历史-文件json.py')

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('"""' + '\n')
        json.dump(dict(sorted_files), f, ensure_ascii=False, indent=4)
        f.write('"""' + '\n')

    # 按日期组织文件
    date_to_files = get_files_by_commit_date(file_commit_times)
    # 按照提交时间排序文件
    sorted_files = sorted(date_to_files.items(), key=lambda x: x[0], reverse=True)

    output_file = os.path.join(repo_directory+'/history', '本地提交历史-时间json.py')

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('""""'+'\n')
        json.dump(dict(sorted_files), f, ensure_ascii=False, indent=4)
        f.write('"""' + '\n')

