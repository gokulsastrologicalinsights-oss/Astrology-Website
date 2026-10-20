import http from "node:http";
import { spawn } from "node:child_process";
import path from "node:path";

const CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";
const CDP_PORT = 9222;
const tempProfileDir = path.join(process.env.TEMP || "C:\\Temp", "chrome-test-" + Date.now());

function getJson(url) {
  return new Promise((resolve, reject) => {
    http.get(url, (res) => {
      let data = "";
      res.on("data", (c) => data += c);
      res.on("end", () => resolve(JSON.parse(data)));
    }).on("error", reject);
  });
}

(async () => {
  const chromeProcess = spawn(CHROME_PATH, [
    "--headless=new",
    "--remote-debugging-port=" + CDP_PORT,
    "--user-data-dir=" + tempProfileDir,
    "--disable-gpu",
    "about:blank"
  ]);
  await new Promise(r => setTimeout(r, 2000));
  const targets = await getJson("http://127.0.0.1:" + CDP_PORT + "/json");
  const target = targets.find(t => t.type === "page");
  const ws = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise(r => ws.onopen = r);

  let id = 1;
  const callbacks = new Map();
  ws.onmessage = (e) => {
    const msg = JSON.parse(e.data);
    if (msg.id && callbacks.has(msg.id)) {
      callbacks.get(msg.id)(msg.result);
      callbacks.delete(msg.id);
    } else if (msg.method === "Runtime.consoleAPICalled") {
      console.log("[CONSOLE]", msg.params.type, msg.params.args.map(a => a.value || a.description || JSON.stringify(a)).join(" "));
    } else if (msg.method === "Runtime.exceptionThrown") {
      console.log("[EXCEPTION]", JSON.stringify(msg.params.exceptionDetails));
    }
  };
  const send = (m, p = {}) => new Promise((resolve) => {
    const cur = id++;
    callbacks.set(cur, resolve);
    ws.send(JSON.stringify({ id: cur, method: m, params: p }));
  });

  await send("Page.enable");
  await send("Runtime.enable");

  // Sign in via /api/auth/login to get cookies
  const loginRes = await fetch("http://127.0.0.1:3000/api/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ identifier: "admin@gokul-astrology.local", password: "Gokul741@" })
  });
  const setCookies = loginRes.headers.getSetCookie();

  for (const cookieStr of setCookies) {
    const parts = cookieStr.split(";").map(s => s.trim());
    const [name, ...valParts] = parts[0].split("=");
    const value = valParts.join("=");
    const cookieObj = {
      name,
      value,
      domain: "127.0.0.1",
      path: "/",
      httpOnly: parts.some(p => p.toLowerCase() === "httponly"),
      secure: parts.some(p => p.toLowerCase() === "secure"),
      sameSite: "Lax"
    };
    await send("Network.setCookie", cookieObj);
  }

  // Navigate directly to remedies with horoscope_id
  await send("Page.navigate", { url: "http://127.0.0.1:3000/remedies?horoscope_id=ba9bb522-a79d-43e8-8493-ac8d53d4d39b" });

  await new Promise(r => setTimeout(r, 6000));

  const diag = await send("Runtime.evaluate", {
    expression: `
      (() => {
        const buttons = Array.from(document.querySelectorAll('button')).map(b => b.innerText.trim());
        const h2s = Array.from(document.querySelectorAll('h2, h3')).map(h => h.innerText.trim());
        return {
          url: window.location.href,
          buttons,
          h2s,
          bodySnippet: document.body.innerText.slice(0, 500)
        };
      })()
    `,
    returnByValue: true
  });

  console.log("DIAG:\n", JSON.stringify(diag.result?.value, null, 2));

  ws.close();
  chromeProcess.kill();
})();
