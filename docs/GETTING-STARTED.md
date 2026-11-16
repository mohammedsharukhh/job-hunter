# Getting started with job-hunter (10 minutes)

No coding needed. You'll install the plugin, give it your resume once, and from then on it works by itself.

---

## What you need
- A **Claude account** (Pro or above for plugins and scheduled tasks)
- **Claude desktop app** (Mac/Windows) — or **Claude Code** if you're a developer
- Your **resume** (PDF or Word)
- Recommended: **Gmail or Outlook** connected, and the **Claude in Chrome** extension

---

## Step 1 — Install the plugin

**Claude desktop app**
1. Go to the [latest release](https://github.com/<owner>/job-hunter/releases/latest) and download **`job-hunter.plugin`**.
2. Double-click it (or drag it into Claude). Click **Install**.

**Claude Code**
```
/plugin marketplace add <owner>/job-hunter
/plugin install job-hunter@job-hunter-marketplace
```

## Step 2 — Connect your tools (recommended)

| Connect | Why | How |
|---|---|---|
| Gmail / Outlook | Send applications, read replies | Claude → Settings → Connectors |
| Claude in Chrome | Fill in career portals, read LinkedIn/Naukri with your own login | Install the Chrome extension |
| Google Calendar | Add interviews | Settings → Connectors |

Everything works without these too — Claude will give you drafts to send yourself.

## Step 3 — Set up (once)

Open a new chat, attach your resume and type:

> **set up job hunter**

Claude will ask a few short questions:
- Which roles? *(e.g. iOS Developer, Mobile Engineer)*
- Which cities / remote? *(e.g. Bangalore, Doha, Remote)*
- Experience level and notice period
- Companies you'd love to work at *(for the hourly watchlist)*
- How many emails per day, and what time to run each day

Then it creates your private `job-hunt` folder and turns on the schedules. **That's the last command you need.**

---

## What happens every day (automatically)

| When | What Claude does |
|---|---|
| Morning | Sends you a short brief: interviews, deadlines, replies, new matches |
| Every hour | Checks your watchlist companies for brand-new jobs |
| Daily run | Finds jobs → writes a tailored resume for each → tests it → prepares applications and emails |
| You | Get **one table** to approve — tick the ones you want |
| After approval | Applications and emails go out **one by one**, a few minutes apart |
| Whenever you open Claude | It picks up where it left off and reminds you of anything urgent |

## Things you can say any time

| Say | You get |
|---|---|
| `tailor my resume to this job: <paste>` | A tailored resume + match score + gaps |
| `check my resume for ATS` (attach it) | A score out of 100 and what to fix |
| `watch Swiggy, Zoho and Careem for iOS jobs` | Added to the hourly watchlist |
| `check my job emails` | Replies sorted, answers drafted |
| `prep me for my interview with <company>` | Research + likely questions + mock interview |
| `I got an offer — is it fair?` | Salary check + negotiation email |
| `find me a referral at <company>` | Your connections there + a message to send |
| `show my dashboard` | Applied, response rate, interviews, follow-ups |
| `what's working?` | Which sources and resume styles get replies |
| `improve my LinkedIn` | Headline, About section, skills |
| `pause job hunter` / `resume job hunter` | Stop / restart all automatic runs |

## Your data
Everything lives in a `job-hunt` folder in your home directory on your computer: your profile, tracker, and one folder per application (job description, resume, cover letter). Nothing is shared unless you choose to.

## Stuck?
See the [FAQ & troubleshooting](FAQ.md) or [open an issue](https://github.com/<owner>/job-hunter/issues/new/choose).
