import json
import os
from github import Github
import datetime
import calendar

with open('repograph_config.json', 'r') as f:
    config = json.load(f)

USER = config['USER']
REPO = config['REPO']
SINCE = config['SINCE']

def get_contributions(github_token, user, repo):
    g = Github(github_token)
    repository = g.get_repo(f'{user}/{repo}')
    
    now = datetime.datetime.now()
    start_date = now - datetime.timedelta(days=SINCE)
    
    commits = repository.get_commits(since=start_date)
    
    contributions = {}
    for commit in commits:
        date_str = commit.commit.author.date.strftime('%Y-%m-%d')
        additions = commit.stats.additions
        deletions = commit.stats.deletions
        changes = additions - deletions
        if date_str in contributions:
            contributions[date_str] += changes
        else:
            contributions[date_str] = changes
    
    print(f"Proceeded {len(commits)} commits.")
    return contributions

def generate_svg(contributions):
    svg_width = 31 + SINCE / 7 * 14
    svg_height = 120
    rect_size = 10
    spacing = 2

    svg = f'<svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">'
    svg += '<style> .day { font: 10px sans-serif; fill: #aaa; } .month { font: 10px sans-serif; fill: #aaa; } </style>'
    
    svg += f'<rect width="{svg_width-1}" height="{svg_height-1}" rx="4" ry="4" fill="none" stroke="#ddd" stroke-width="1"/>'
    
    now = datetime.datetime.now()
    start_date = now - datetime.timedelta(days=SINCE)
    date_list = [start_date + datetime.timedelta(days=x) for x in range(0, SINCE)]
    
    x = 30 
    y = 20
    for date in date_list:
        date_str = date.strftime('%Y-%m-%d')
        count = contributions.get(date_str, 0)
        
        if count == 0:
            color = '#ebedf0'
        elif count < 5:
            color = '#c6e48b'
        elif count < 10:
            color = '#7bc96f'
        elif count < 20:
            color = '#239a3b'
        else:
            color = '#196127'
        
        day_of_week = date.weekday()
        if day_of_week == 0:
            x += rect_size + spacing
            y = 20
        
        svg += f'<rect x="{x}" y="{y}" width="{rect_size}" height="{rect_size}" fill="{color}" rx="2" ry="2"/>'
        
        y += rect_size + spacing

    month_names = [calendar.month_abbr[i] for i in range(1, 13)]
    current_month = start_date.month
    for date in date_list:
        if date.day == 1:
            month_name = month_names[date.month - 1]
            month_x = 30 + (date - start_date).days // 7 * (rect_size + spacing)
            svg += f'<text x="{month_x}" y="15" class="month">{month_name}</text>'
    
    day_names = ['Mon', 'Wed', 'Fri', 'Sun']
    for i, day_name in enumerate(day_names):
        svg += f'<text x="5" y="{30 + i * 1.95 * (rect_size + spacing)}" class="day">{day_name}</text>'
    
    svg += '</svg>'
    
    return svg

if __name__ == '__main__':
    github_token = os.getenv('CUSTOM_TOKEN')
    contributions = get_contributions(github_token, USER, REPO, SINCE)
    svg = generate_svg(contributions)
    
    with open('repograph.svg', 'w') as f:
        f.write(svg)

    print("SVG file 'repograph.svg' has been generated.")