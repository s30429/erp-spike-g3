const $ = (id) => document.getElementById(id);

async function loadWhale() {
  const w = await (await fetch("/admin/whale")).json();
  $("whale-state").textContent = w.present ? `in the database (${w.orders.toLocaleString("en-US")} orders)` : "removed from the database";
  $("whale-remove").disabled = !w.present;
  $("whale-add").disabled = w.present;
}

async function whaleAction(kind, busyText) {
  $("whale-remove").disabled = $("whale-add").disabled = true;
  $("whale-msg").textContent = busyText;
  await fetch(`/admin/whale/${kind}`, { method: "POST" });
  $("whale-msg").textContent = kind === "remove" ? "Whale removed." : "Whale added.";
  loadWhale();
}

async function loadSim() {
  const s = await (await fetch("/admin/simulation")).json();
  $("sim-state").textContent = s.running ? "running: the whale is generating reports" : "off";
  $("sim-toggle").textContent = s.running ? "Stop simulation" : "Simulate month-end";
  $("sim-toggle").className = s.running ? "ghost" : "";
}

$("whale-remove").addEventListener("click", () => whaleAction("remove", "Removing whale data..."));
$("whale-add").addEventListener("click", () => whaleAction("add", "Adding whale data (about 15 seconds)..."));
$("sim-toggle").addEventListener("click", async () => {
  const running = $("sim-toggle").textContent.startsWith("Stop");
  await fetch(`/admin/simulation/${running ? "stop" : "start"}`, { method: "POST" });
  loadSim();
});

loadWhale();
loadSim();
