const state = {
  token: localStorage.getItem("securevault_token"),
  profile: null,
  activeOrder: null,
  pollTimer: null,
  theme: localStorage.getItem("securevault_theme") || "light",
};

const views = {
  overview: document.getElementById("overviewView"),
  profile: document.getElementById("profileView"),
  wallet: document.getElementById("walletView"),
  premium: document.getElementById("premiumView"),
  admin: document.getElementById("adminView"),
};

const pageTitles = {
  overview: "Overview",
  profile: "Profile",
  wallet: "Local Wallet",
  premium: "Premium",
  admin: "Admin Console",
};

const authPanel = document.getElementById("authPanel");
const appPanel = document.getElementById("appPanel");
const toast = document.getElementById("toast");

function showToast(message) {
  toast.textContent = message;
  toast.classList.remove("hidden");
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => toast.classList.add("hidden"), 3600);
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => (
    {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#039;",
    }[char]
  ));
}

function headers() {
  return {
    Authorization: `Bearer ${state.token}`,
  };
}

async function api(path, options = {}) {
  const response = await fetch(path, options);
  let data = {};

  try {
    data = await response.json();
  } catch {
    data = { detail: "Server returned an invalid response." };
  }

  if (!response.ok) {
    throw new Error(data.detail || data.error || "Request failed.");
  }

  return data;
}

function setAuthMode(mode) {
  const isLogin = mode === "login";
  document.getElementById("loginForm").classList.toggle("hidden", !isLogin);
  document.getElementById("registerForm").classList.toggle("hidden", isLogin);
  document.getElementById("loginTab").classList.toggle("active", isLogin);
  document.getElementById("registerTab").classList.toggle("active", !isLogin);
}

function setView(name) {
  Object.entries(views).forEach(([key, view]) => {
    view.classList.toggle("active", key === name);
  });

  document.querySelectorAll(".nav-item").forEach((item) => {
    item.classList.toggle("active", item.dataset.view === name);
  });

  document.getElementById("pageTitle").textContent = pageTitles[name];

  if (name === "admin") {
    loadAdminDashboard();
  }
}

function setTheme(theme) {
  state.theme = theme;
  localStorage.setItem("securevault_theme", theme);
  document.body.dataset.theme = theme;

  document.querySelectorAll("[data-theme]").forEach((item) => {
    item.classList.toggle("active", item.dataset.theme === theme);
  });
}

function renderProfile() {
  const profile = state.profile;
  const isAdmin = profile?.role === "admin";

  authPanel.classList.add("hidden");
  appPanel.classList.remove("hidden");

  document.getElementById("sessionName").textContent = profile.username;
  document.getElementById("sessionMeta").textContent = `${profile.role.toUpperCase()} / ${profile.subscription.toUpperCase()}`;
  document.getElementById("profileUsername").textContent = profile.username;
  document.getElementById("profileRole").textContent = profile.role.toUpperCase();
  document.getElementById("profileSubscription").textContent = profile.subscription.toUpperCase();
  document.getElementById("profileSettingsUsername").textContent = profile.username;
  document.getElementById("profileSettingsRole").textContent = profile.role.toUpperCase();
  document.getElementById("profileSettingsSubscription").textContent = profile.subscription.toUpperCase();

  document.querySelectorAll(".admin-only").forEach((element) => {
    element.classList.toggle("hidden", !isAdmin);
  });
}

async function loadProfile() {
  if (!state.token) {
    return;
  }

  try {
    state.profile = await api("/profile", { headers: headers() });
    renderProfile();
  } catch (error) {
    logout(false);
    showToast(error.message);
  }
}

function logout(showMessage = true) {
  state.token = null;
  state.profile = null;
  localStorage.removeItem("securevault_token");
  appPanel.classList.add("hidden");
  authPanel.classList.remove("hidden");
  document.getElementById("sessionName").textContent = "Guest";
  document.getElementById("sessionMeta").textContent = "Not authenticated";
  window.clearInterval(state.pollTimer);

  if (showMessage) {
    showToast("Logged out.");
  }
}

function params(values) {
  const search = new URLSearchParams();
  Object.entries(values).forEach(([key, value]) => search.set(key, value));
  return search;
}

async function registerUser(event) {
  event.preventDefault();
  const username = document.getElementById("registerUsername").value.trim();
  const password = document.getElementById("registerPassword").value;

  try {
    const data = await api(`/register?${params({ username, password })}`, { method: "POST" });
    showToast(data.message);
    setAuthMode("login");
    document.getElementById("loginUsername").value = username;
  } catch (error) {
    showToast(error.message);
  }
}

async function loginUser(event) {
  event.preventDefault();
  const username = document.getElementById("loginUsername").value.trim();
  const password = document.getElementById("loginPassword").value;

  try {
    const data = await api(`/login?${params({ username, password })}`, { method: "POST" });
    state.token = data.access_token;
    localStorage.setItem("securevault_token", state.token);
    await loadProfile();
    showToast("Login successful.");
  } catch (error) {
    showToast(error.message);
  }
}

async function changePassword(event) {
  event.preventDefault();
  const currentPassword = document.getElementById("currentPassword").value;
  const newPassword = document.getElementById("newPassword").value;

  try {
    const data = await api(`/change-password?${params({ current_password: currentPassword, new_password: newPassword })}`, {
      method: "POST",
      headers: headers(),
    });
    document.getElementById("changePasswordForm").reset();
    showToast(data.message);
  } catch (error) {
    showToast(error.message);
  }
}

function toHex(buffer) {
  return [...new Uint8Array(buffer)].map((byte) => byte.toString(16).padStart(2, "0")).join("");
}

function fromHex(hex) {
  const bytes = new Uint8Array(hex.length / 2);
  for (let index = 0; index < bytes.length; index += 1) {
    bytes[index] = parseInt(hex.slice(index * 2, index * 2 + 2), 16);
  }
  return bytes;
}

async function deriveKey(password, salt, usage) {
  const baseKey = await crypto.subtle.importKey(
    "raw",
    new TextEncoder().encode(password),
    "PBKDF2",
    false,
    ["deriveKey"],
  );

  return crypto.subtle.deriveKey(
    {
      name: "PBKDF2",
      salt,
      iterations: 200000,
      hash: "SHA-256",
    },
    baseKey,
    { name: "AES-GCM", length: 256 },
    false,
    usage,
  );
}

async function createWallet() {
  const password = document.getElementById("walletPassword").value;
  if (!password) {
    showToast("Enter a wallet password first.");
    return;
  }

  const privateBytes = crypto.getRandomValues(new Uint8Array(32));
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const key = await deriveKey(password, salt, ["encrypt"]);
  const encrypted = await crypto.subtle.encrypt({ name: "AES-GCM", iv }, key, privateBytes);
  const digest = await crypto.subtle.digest("SHA-256", privateBytes);
  const address = `SV-${toHex(digest).slice(0, 36).toUpperCase()}`;

  localStorage.setItem(
    "securevault_wallet",
    JSON.stringify({
      address,
      salt: toHex(salt),
      iv: toHex(iv),
      encrypted: toHex(encrypted),
    }),
  );

  document.getElementById("walletAddress").textContent = address;
  document.getElementById("walletPassword").value = "";
  showToast("Local wallet created.");
}

function loadWalletAddress() {
  const wallet = JSON.parse(localStorage.getItem("securevault_wallet") || "null");
  document.getElementById("walletAddress").textContent = wallet?.address || "No wallet created yet.";
}

async function signMessage() {
  const wallet = JSON.parse(localStorage.getItem("securevault_wallet") || "null");
  const password = document.getElementById("signPassword").value;
  const message = document.getElementById("messageToSign").value;

  if (!wallet) {
    showToast("Create a local wallet first.");
    return;
  }

  if (!password || !message) {
    showToast("Enter both wallet password and message.");
    return;
  }

  try {
    const key = await deriveKey(password, fromHex(wallet.salt), ["decrypt"]);
    const privateBytes = await crypto.subtle.decrypt(
      { name: "AES-GCM", iv: fromHex(wallet.iv) },
      key,
      fromHex(wallet.encrypted),
    );
    const hmacKey = await crypto.subtle.importKey(
      "raw",
      privateBytes,
      { name: "HMAC", hash: "SHA-256" },
      false,
      ["sign"],
    );
    const signature = await crypto.subtle.sign("HMAC", hmacKey, new TextEncoder().encode(message));
    document.getElementById("signatureOutput").textContent = toHex(signature);
    showToast("Message signed locally.");
  } catch {
    showToast("Invalid wallet password or corrupted local wallet.");
  }
}

async function subscribe() {
  try {
    const data = await api("/create-order", { method: "POST", headers: headers() });
    state.activeOrder = data.order_id;
    document.getElementById("paymentStatus").textContent = `Order created: ${state.activeOrder}`;
    window.open(data.payment_url, "_blank", "noopener");
    startPaymentPolling();
  } catch (error) {
    showToast(error.message);
  }
}

function startPaymentPolling() {
  window.clearInterval(state.pollTimer);
  state.pollTimer = window.setInterval(async () => {
    if (!state.activeOrder) {
      return;
    }

    const data = await api(`/payment-status/${state.activeOrder}`);
    document.getElementById("paymentStatus").textContent = `Payment status: ${data.status}`;

    if (data.status === "success") {
      window.clearInterval(state.pollTimer);
      await api("/verify-payment", { method: "POST", headers: headers() });
      await loadProfile();
      showToast("Premium activated.");
    }

    if (data.status === "failed") {
      window.clearInterval(state.pollTimer);
      showToast("Payment failed. Please try again.");
    }
  }, 3000);
}

async function loadAdminDashboard() {
  if (state.profile?.role !== "admin") {
    showToast("Admin access is required.");
    setView("overview");
    return;
  }

  try {
    const data = await api("/admin/dashboard", { headers: headers() });
    document.getElementById("totalUsers").textContent = data.summary.total_users;
    document.getElementById("premiumUsers").textContent = data.summary.premium_users;
    document.getElementById("adminUsers").textContent = data.summary.admin_users;
    document.getElementById("usersTable").innerHTML = data.users
      .map((user) => (
        `<tr><td>${escapeHtml(user.username)}</td><td>${escapeHtml(user.role)}</td><td>${escapeHtml(user.subscription)}</td></tr>`
      ))
      .join("");
  } catch (error) {
    showToast(error.message);
  }
}

async function adminAction(endpoint) {
  const username = document.getElementById("adminUsername").value.trim();
  if (!username) {
    showToast("Enter a username first.");
    return;
  }

  try {
    const data = await api(`${endpoint}?${params({ username })}`, {
      method: "POST",
      headers: headers(),
    });
    showToast(data.message);
    await loadAdminDashboard();
  } catch (error) {
    showToast(error.message);
  }
}

document.getElementById("loginTab").addEventListener("click", () => setAuthMode("login"));
document.getElementById("registerTab").addEventListener("click", () => setAuthMode("register"));
document.getElementById("registerForm").addEventListener("submit", registerUser);
document.getElementById("loginForm").addEventListener("submit", loginUser);
document.getElementById("changePasswordForm").addEventListener("submit", changePassword);
document.getElementById("logoutButton").addEventListener("click", () => logout());
document.getElementById("createWalletButton").addEventListener("click", createWallet);
document.getElementById("signButton").addEventListener("click", signMessage);
document.getElementById("subscribeButton").addEventListener("click", subscribe);
document.getElementById("refreshAdminButton").addEventListener("click", loadAdminDashboard);
document.getElementById("copyAddressButton").addEventListener("click", async () => {
  const address = document.getElementById("walletAddress").textContent;
  if (address && !address.startsWith("No wallet")) {
    await navigator.clipboard.writeText(address);
    showToast("Wallet address copied.");
  }
});

document.querySelectorAll(".nav-item").forEach((item) => {
  item.addEventListener("click", () => setView(item.dataset.view));
});

document.querySelectorAll("[data-jump]").forEach((item) => {
  item.addEventListener("click", () => setView(item.dataset.jump));
});

document.querySelectorAll("[data-admin-action]").forEach((item) => {
  item.addEventListener("click", () => adminAction(item.dataset.adminAction));
});

document.querySelectorAll("[data-theme]").forEach((item) => {
  item.addEventListener("click", () => setTheme(item.dataset.theme));
});

setTheme(state.theme);
loadWalletAddress();
loadProfile();
