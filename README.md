# Mini-ERP: the whale customer

This is a small demo of a cloud business system (an "ERP") used in the exercise
*Refinement of the Whale*. You do not need to read or understand any code to use it.

## The business situation

You run a cloud ERP for small businesses. Every customer (called a *tenant*) has 5 to 20
users who enter orders and look at reports.

- **300 small customers** pay about €99 a month each.
- All of them share **one system and one database**. This keeps costs low.
- A distributor with **1,200 users** wants to join. They would pay **€6,000 a month**
  on a 12-month contract. We call this big customer **the whale**.
- They require **99.9% availability** (a promise that the system works almost all the time)
  and **separation of their data** from everyone else's.

The catch: the system was never built for a customer this big. In a test it had to handle
about 8 times today's peak load, and the database grew by 35%. Worst of all, the whale's
**month-end reports** slowed the test system down for everybody else.

Sales needs a go / no-go decision within a week. The question for the exercise:
**can we take on the whale without hurting our 300 small customers, and what would it cost?**

## What the application shows

The application has two pages.

**Customer** (the main page). This is what one customer sees: their latest orders, a form
for a new order, and a button that creates the monthly report. The label *System speed* in
the top bar shows how long the last action took (green is fast, red is slow).

**Operations.** A control panel for setting up the situation:

- **Remove whale / Add whale** takes the big customer out of the system or puts them back.
- **Simulate month-end** makes the whale's finance team run their monthly reports all at
  once, as they would on the last day of the month.

### Try it yourself

1. Open the **Customer** page and click around as a small customer. Everything is fast.
2. Open **Operations** and click **Simulate month-end**.
3. Go back to the **Customer** page and try again. The system is now slow, and after a few
   seconds the page stops working. This is what the small customers would experience.
4. On **Operations**, click **Remove whale**. Now the small customer's page works again,
   even though the simulation is still running.
5. Click **Add whale** (it takes about 15 seconds) and **Stop simulation** to restore everything.

This is the problem you are asked to solve.

## How to run it

The easiest way is in your web browser. You do not need to install anything.

1. Log in to GitHub and open this repository.
2. Choose your own branch from the branch list at the top left of the repository page.
3. Click the green **Code** button, open the **Codespaces** tab and choose
   **Create codespace on** your branch.
4. Wait a few minutes. The first start builds the application and loads the data.
   When it is ready, a browser tab with the application opens on its own.
5. If it did not open, find the **Ports** tab at the bottom of the screen and click the
   globe icon next to port **8000**.

Notes:

- A Codespace uses your free monthly hours. When you finish, stop it
  (github.com/codespaces, then **Stop codespace**). It also stops by itself after 30
  minutes without activity.
- Pages: the main page is the address of port 8000, and **Operations** is the same address
  followed by `/ops`.

### Running on your own computer (optional)

If you have Docker Desktop installed and running, open a terminal in the project folder and run:

```bash
docker compose up -d --build
```

```bash
docker compose run --rm api python -m app.seed
```

Then open <http://localhost:8000> in your browser. To switch it off:

```bash
docker compose down
```
