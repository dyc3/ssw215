#!/usr/bin/env python3
import requests
import datetime
import redis
import os
import json
from urllib.parse import urlparse, urlencode, parse_qsl, urlunparse

with open("token", "r") as f:
	TOKEN = ''.join(f.readlines()).strip()

BASE_URL = "https://api.github.com"
r = redis.Redis(db=os.getenv("REDIS_DB") or 5)

def cached_get_page(url_str: str, page: int, redis_key_pfx: str):
	assert len(redis_key_pfx) > 0
	cached_etag = r.get(f"{redis_key_pfx}:{page}:etag")

	url_parts = list(urlparse(url_str))
	query = dict(parse_qsl(url_parts[4]))
	query.update({
		"page": page,
		"perpage": 100,
	})
	url_parts[4] = urlencode(query)
	url = urlunparse(url_parts)

	resp = requests.get(url, headers={
		"Authorization": f"token {TOKEN}",
		"If-None-Match": cached_etag,
		"accept": "application/vnd.github.v3+json",
	})
	print(f"rate limit: {resp.headers['X-RateLimit-Remaining']}/{resp.headers['X-RateLimit-Limit']} reset at {datetime.datetime.fromtimestamp(int(resp.headers['X-RateLimit-Reset']))}")
	# print(f"link header: {resp.headers['Link']}")
	if resp.status_code >= 400:
		print(f"get paged resource failed: {resp.status_code} {resp.json()}")
		return []
	if resp.status_code == 304:
		print(f"cache hit: {redis_key_pfx} page {page}")
		payload = r.get(f"{redis_key_pfx}:{page}:result")
	elif resp.status_code == 200:
		payload = resp.text
		print(f"cache miss: {redis_key_pfx} page {page}")
		r.set(f"{redis_key_pfx}:{page}:result", payload)
		r.set(f"{redis_key_pfx}:{page}:etag", resp.headers.get("ETag"))
	return json.loads(payload)

def cached_get_one(url: str, redis_key_pfx: str, media_type: str="application/vnd.github.v3+json"):
	assert len(redis_key_pfx) > 0
	cached_etag = r.get(f"{redis_key_pfx}:etag")

	resp = requests.get(url, headers={
		"Authorization": f"token {TOKEN}",
		"If-None-Match": cached_etag,
		"accept": media_type,
	})
	print(f"rate limit: {resp.headers['X-RateLimit-Remaining']}/{resp.headers['X-RateLimit-Limit']} reset at {datetime.datetime.fromtimestamp(int(resp.headers['X-RateLimit-Reset']))}")
	# print(f"link header: {resp.headers['Link']}")
	if resp.status_code >= 400:
		print(f"get resource failed: {resp.status_code} {resp.json()}")
		return None
	if resp.status_code == 304:
		print(f"cache hit: {redis_key_pfx}")
		payload = r.get(f"{redis_key_pfx}:result")
	elif resp.status_code == 200:
		payload = resp.text
		print(f"cache miss: {redis_key_pfx}")
		r.set(f"{redis_key_pfx}:result", payload)
		r.set(f"{redis_key_pfx}:etag", resp.headers.get("ETag"))
	return json.loads(payload)

def get_all_events(username):
	page = 0
	url = f"{BASE_URL}/users/{username}/events/public"
	while True:
		events = cached_get_page(url, page, f"events:{username}")
		if not events:
			break

		for event in events:
			if isinstance(event, str):
				print(f"what the fuck? got {event}")
				continue
			yield event
		page += 1

def get_filtered_events(username, types=["PushEvent", "PullRequestEvent"], since=None):
	if since:
		since_time = datetime.datetime.fromisoformat(since)
	events = get_all_events(username)
	if not events:
		return []
	for event in events:
		if event["type"] not in types:
			continue
		if since:
			event_time = parse_gh_time(event['created_at'])
			if event_time < since_time:
				continue
		yield event

def get_commits(repo: dict, author: str, since=None, branch=None):
	page = 0
	while True:
		if branch:
			commits = cached_get_page(f"{repo['url']}/commits?author={author}&since={since}&sha={branch}", page, f"commits:{repo['name']}:{author}:{branch}")
		else:
			commits = cached_get_page(f"{repo['url']}/commits?author={author}&since={since}", page, f"commits:{repo['name']}:{author}")
		if not commits:
			break
		for commit in commits:
			yield commit

		page += 1

def parse_gh_time(s) -> datetime.datetime:
	return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")

ext_to_language = {
	"py": "Python",
	"go": "Go",
	"html": "HTML",
	"css": "CSS",
	"js": "javascript",
	"jsx": "javascript",
	"vue": "Vue",
	"ts": "typescript",
	"tsx": "typescript",
	"rs": "Rust",
	"c": "C",
	"cpp": "C++",
	"sh": "Bash",
	"json": "json",
	"csv": "csv",
	"md": "markdown",
	"yml": "yaml",
	"yaml": "yaml",
}
IGNORE_EXTS = ["mod", "sum", "gitignore", "gitmodules", "jpg", "jpeg", "png", "gif", "mp4", "tour"]

if __name__ == "__main__":
	USERNAME = 'dyc3'
	SINCE = '2021-03-11'
	repos = {}
	for event in get_filtered_events(USERNAME, since=SINCE):
		repos[event['repo']['name']] = event['repo']
		print(f"event: {event['id']} {event['type'].ljust(20)} {event['repo']['name'].ljust(30)} {event['created_at']}")
	repos = list(repos.values())
	print(f"repos: {repos}")

	max_time_delta = datetime.timedelta(hours=3)

	coding_sessions = []
	for repo in repos:
		current_session = []
		def push_session():
			global coding_sessions
			global current_session
			coding_sessions += [{
				"repo": repo,
				"commits": current_session[::-1],
				"duration": None,
				"additions": 0,
				"deletions": 0,
				"languages": set(),
			}]
			current_session = []
		repo_data = cached_get_one(repo['url'], f"repo:{repo['name']}")

		# for commit in get_commits(repo, USERNAME, since=SINCE, branch=repo_data['default_branch']):
		for commit in get_commits(repo, USERNAME, since=SINCE):
			print(f"commit: {commit['sha']} {commit['author']['login']} {commit['commit']['author']['date']} {commit['committer']['login']}")
			if not current_session:
				current_session = [commit]
				continue
			last_commit_time = parse_gh_time(current_session[-1]['commit']['author']['date'])
			commit_time = parse_gh_time(commit['commit']['author']['date'])
			# print(f"delta: {last_commit_time - commit_time}")
			delta = last_commit_time - commit_time
			if delta >= datetime.timedelta(0) and delta <= max_time_delta:
				current_session += [commit]
			else:
				push_session()
		if current_session:
			push_session()

	min_session_time = datetime.timedelta(minutes=20)

	total_time = datetime.timedelta(0)
	total_commits = 0
	total_additions = 0
	total_deletions = 0
	for i, session in enumerate(coding_sessions):
		first_commit_time = parse_gh_time(session["commits"][0]['commit']['author']['date'])
		last_commit_time = parse_gh_time(session["commits"][-1]['commit']['author']['date'])
		delta = last_commit_time - first_commit_time
		assert delta >= datetime.timedelta(0)
		duration = max(delta, min_session_time) # + datetime.timedelta(minutes=20)
		print(f"session {i}: {session['repo']['name']} {len(session['commits'])} commits, {duration}")
		total_time += duration
		session["duration"] = duration

		# compile lines of code, languages
		total_commits += len(session['commits'])
		for commit in session['commits']:
			data = cached_get_one(commit['url'], f"commit:{session['repo']['name']}:{commit['sha']}")
			if not data:
				print(f"commit doesn't exist? {session['repo']['name']} {commit['sha']}")
				continue

			session["additions"] += data['stats']['additions']
			session["deletions"] += data['stats']['deletions']
			for file in data['files']:
				if file['filename'].startswith(".") or '.' not in file['filename']:
					continue
				ext = file['filename'].split(".")[-1]
				if ext in IGNORE_EXTS:
					continue
				session["languages"] |= {ext_to_language[ext]}
		total_additions += session["additions"]
		total_deletions += session["deletions"]

	print("Summary:")
	print(f"{len(coding_sessions)} coding sessions for a total of {total_time}")
	print(f"{len(repos)} repos")
	print(f"\t{total_commits} commits")
	print(f"\t{total_additions} additions")
	print(f"\t{total_deletions} deletions")

	# output csv
	with open("logbook.csv", "w") as f:
		f.write(f"date,project,languages,lines of code,time spent,reflection\n")
		for session in coding_sessions:
			reflection = ', '.join([c['commit']['message'].replace("\n", " ") for c in session['commits']])
			languages = ', '.join(session['languages'])
			f.write(f"{session['commits'][0]['commit']['author']['date']},{session['repo']['name']},\"{languages}\",+{session['additions']} / -{session['deletions']},{session['duration']},\"{reflection}\"\n")
