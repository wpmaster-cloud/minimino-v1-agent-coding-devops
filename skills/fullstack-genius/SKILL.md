---
name: fullstack-genius
description: "Advanced Git-based team coordination protocol for multi-agent 'coding' teams. Learn how to pull from teammates, integrate code, and assign missions."
---

# Fullstack Genius Coordination Protocol

You are part of the elite `coding` team. You work within a structure that includes a Project Manager (PM), Frontend, Backend, Reviewer, QA, and DevOps agents. Your common goal is to build fullstack software perfectly via asynchronous, decentralized Git orchestration.

**Only the Project Manager (`pm`) communicates directly with the human user.**
The PM breaks down requirements and uses `send_mission` to delegate work to the frontend and backend engineers. Once features are developed, they are sent to the reviewer and QA, and finally handed to DevOps for deployment.

Your personal workspace is physically separated from your teammates. Each agent pushes code to its own unique GitHub repository (initialized automatically in `/workspace`). 

**Your repository matches your name:** `wpmaster-cloud/minimino-v1-agent-coding-{YOUR_NAME}`.
**Your teammates' repositories are:** `wpmaster-cloud/minimino-v1-agent-coding-{THEIR_NAME}`.

## Step 1: Push Your Own Work Regularly
Whenever you reach a milestone or finish a small chunk of work, commit and push it to your own repository so others can see it:
```bash
git add -A && git commit -m "[your agent role] implemented feature X" && git push
```

## Step 2: Fetching Teammates' Code
To seamlessly integrate features (e.g., frontend needing backend's API), you must actively pull code from your teammates' repositories. 

Add their remote repository:
```bash
git remote add backend https://x-access-token:${GITHUB_TOKEN}@github.com/wpmaster-cloud/minimino-v1-agent-coding-backend.git
git fetch backend main
```

Merge their branch into your workspace:
```bash
git merge backend/main --allow-unrelated-histories
# Fix any merge conflicts, then commit
```

## Step 3: Pinging Teammates via `send_mission`
Once you push code that requires action from another agent (e.g., asking the `reviewer` to check your work, or asking `frontend` to consume your new backend API), use the `send_mission` tool.

Target the exact name of your teammate (`frontend`, `backend`, `reviewer`, `qa`, or `devops`).
**Example mission to send to QA:**
> "I have just pushed the new Authentication API to my remote (wpmaster-cloud/minimino-v1-agent-coding-backend). Please pull from my repository and run the test suite against it."

## Step 4: Act on Incoming Requests
When someone sends *you* a mission, you must immediately act on it. Use `run_command` with `git remote` and `git fetch` to grab the specific code they mentioned, execute your specific role (Review, test, deploy, consume), and report back.

## Best Practices
- Never overwrite each other's work blindly. Rely on `git merge` and fix conflicts properly.
- Ensure your `package.json` and requirements stay synchronized.
- Don't use placeholders. Build real applications.
- If a team member is unresponsive, use `worker_status` and `worker_events` to check what they are doing before pinging them again.
