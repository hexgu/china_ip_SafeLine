import requests
import math
import os
import re

def download_ip_list(url):
    """Download IP list from given URL and remove comments"""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return [
            line.strip()
            for line in response.text.splitlines()
            if line.strip() and not line.strip().startswith('#')
        ]
    except requests.RequestException as e:
        print(f"Error downloading from {url}: {e}")
        return []

def calculate_num_parts(total_ips, max_per_file=1000):
    """Calculate how many parts we need to ensure each file has ≤1000 IPs"""
    return math.ceil(total_ips / max_per_file)

def split_list_evenly(ip_list, prefix):
    """Split IP list into appropriate number of parts"""
    total_ips = len(ip_list)
    num_parts = calculate_num_parts(total_ips)
    print(f"Splitting into {num_parts} parts to ensure each file has no more than 1000 IPs")

    base_size = total_ips // num_parts
    remainder = total_ips % num_parts

    created_files = []
    start = 0
    for i in range(num_parts):
        current_part_size = base_size + (1 if i < remainder else 0)
        end = start + current_part_size

        current_ips = ip_list[start:end]
        filename = f'{prefix}_part_{i+1}.txt'

        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(current_ips))

        created_files.append(filename)
        print(f"Created {filename} with {len(current_ips)} IPs")
        start = end

    return created_files

def update_readme_sections(ipv4_files, ipv6_files, blackip_files):
    """Update specific sections in README.md while preserving the rest"""
    try:
        with open('README.md', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("README.md not found. Creating new file.")
        content = """# china_ip_SafeLine
SafeLine 社区版社区版只支持 1000 条 ip ，本项目将中国 IP 列表进行分割，适应 SafeLine 社区版社区版 1000 条的要求
## 项目数据来源
[SukkaW/Surge](https://github.com/SukkaW/Surge)  chnroute CIDR
- 自动生成
- IPv4 [原始数据](https://github.com/misakaio/chnroutes2) 由 Misaka Network, Inc. 以 [CC BY-SA 2.0](https://creativecommons.org/licenses/by-sa/2.0/) 协议发布，二次处理补充合并了 Misaka Network, Inc. 收不到 BGP 路由的部分国内段、排除了被 Misaka Network, Inc. 误收的在香港广播的 IP 段（通常由 中国移动国际 CMI 广播）
- IPv6 原始数据 由 [gaoyifan/china-operator-ip](https://github.com/gaoyifan/china-operator-ip) 以 MIT 协议发布
## 使用
### ipv4
### ipv6
### blackip"""

    # 查找各个部分
    sections = re.split(r'(### ipv4|### ipv6|### blackip)', content)

    # 创建新内容
    new_content = []
    for section in sections:
        if section == "### ipv4":
            new_content.append(section + "\n")
            for file in ipv4_files:
                jsdelivr_link = f"https://cdn.jsdelivr.net/gh/hexgu/Rule-Snippe@main/{file}"
                new_content.append(f"- [{file}]({jsdelivr_link})\n")
        elif section == "### ipv6":
            new_content.append(section + "\n")
            for file in ipv6_files:
                jsdelivr_link = f"https://cdn.jsdelivr.net/gh/hexgu/Rule-Snippe@main/{file}"
                new_content.append(f"- [{file}]({jsdelivr_link})\n")
        elif section == "### blackip":
            new_content.append(section + "\n")
            for file in blackip_files:
                jsdelivr_link = f"https://cdn.jsdelivr.net/gh/hexgu/Rule-Snippe@main/{file}"
                new_content.append(f"- [{file}]({jsdelivr_link})\n")
        else:
            new_content.append(section)

    # 写入文件
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(''.join(new_content))

    print("README.md has been updated!")

def main():
    # URLs for IP lists
    ipv4_url = "https://ruleset.skk.moe/Clash/ip/china_ip.txt"
    ipv6_url = "https://ruleset.skk.moe/Clash/ip/china_ip_ipv6.txt"
    blackip_url = "https://blackip.ustc.edu.cn/list.php?txt"

    # Process IPv4 list
    print("\nDownloading IPv4 list...")
    ipv4_list = download_ip_list(ipv4_url)
    print(f"Downloaded {len(ipv4_list)} IPv4 addresses")
    ipv4_files = split_list_evenly(ipv4_list, 'china_ip')

    # Process IPv6 list
    print("\nDownloading IPv6 list...")
    ipv6_list = download_ip_list(ipv6_url)
    print(f"Downloaded {len(ipv6_list)} IPv6 addresses")
    ipv6_files = split_list_evenly(ipv6_list, 'china_ip_ipv6')

    # Process Blackip list
    print("\nDownloading Blackip list...")
    blackip_list = download_ip_list(blackip_url)
    print(f"Downloaded {len(blackip_list)} Blackip addresses")
    blackip_files = split_list_evenly(blackip_list, 'blackip')

    # Update README.md
    update_readme_sections(ipv4_files, ipv6_files, blackip_files)

if __name__ == "__main__":
    main()
