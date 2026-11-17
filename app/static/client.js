const $ = (id) => document.getElementById(id);
const money = (n) => Number(n).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

const TIMEOUT_MS = 5000;

// fetch with a 5 s limit; a slow or failed call throws
async function api(url, options = {}) {
  const t0 = performance.now();
  const r = await fetch(url, { ...options, signal: AbortSignal.timeout(TIMEOUT_MS) });
  showSpeed(Math.round(performance.now() - t0));
  return r;
}

function showSpeed(ms) {
  $("speed").textContent = `${ms} ms`;
  $("speed").className = "badge " + (ms < 500 ? "ok" : ms < 2000 ? "slow" : "bad");
}

function crash(message) {
  $("crash").hidden = false;
  $("crash-msg").textContent = message;
}
window.addEventListener("unhandledrejection", (e) => crash(String(e.reason)));
window.addEventListener("error", (e) => crash(e.message));

function tenantId() { return $("tenant").value; }

async function loadTenants() {
  const tenants = await (await api("/api/tenants")).json();
  $("tenant").innerHTML = tenants
    .map((t) => `<option value="${t.id}" data-plan="${t.plan}">${t.id} - ${t.name}</option>`)
    .join("");
  $("tenant").value = 5;
  showPlan();
  loadOrders();
}

function showPlan() {
  const plan = $("tenant").selectedOptions[0].dataset.plan;
  $("plan").textContent = plan === "enterprise" ? "whale" : "small customer";
  $("plan").className = "badge" + (plan === "enterprise" ? " whale" : "");
}

async function loadOrders() {
  $("orders-msg").textContent = "Loading...";
  const r = await api(`/t/${tenantId()}/orders?limit=10`);
  const rows = await r.json();
  $("orders").innerHTML = rows
    .map((o) => `<tr><td>${o.id}</td><td>${o.order_date}</td><td>${o.status}</td><td class="num">${money(o.total)}</td></tr>`)
    .join("");
  $("orders-msg").textContent = rows.length ? "" : "No orders.";
}

async function addOrder() {
  $("add").disabled = true;
  const body = { lines: [{ product: $("product").value, qty: +$("qty").value, unit_price: $("price").value }] };
  const r = await api(`/t/${tenantId()}/orders`, {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
  });
  await r.json();
  $("add-msg").textContent = "Order added.";
  $("add").disabled = false;
  loadOrders();
}

async function runReport() {
  $("report").disabled = true;
  $("report-msg").textContent = "Calculating...";
  $("report-rows").innerHTML = "";
  const t0 = performance.now();
  const r = await api(`/t/${tenantId()}/reports/monthly`);
  const ms = Math.round(performance.now() - t0);
  const rows = await r.json();
  $("report-msg").textContent = `Done in ${ms} ms (${rows.length} rows, showing 10)`;
  $("report-rows").innerHTML = rows.slice(0, 10)
    .map((x) => `<tr><td>${x.month}</td><td>${x.product}</td><td class="num">${money(x.revenue)}</td></tr>`)
    .join("");
  $("report").disabled = false;
}

$("tenant").addEventListener("change", () => { showPlan(); loadOrders(); $("report-rows").innerHTML = ""; $("report-msg").textContent = ""; });
$("add").addEventListener("click", addOrder);
$("report").addEventListener("click", runReport);
loadTenants();
