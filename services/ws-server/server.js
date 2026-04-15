import http from "node:http";
import { WebSocketServer } from "ws";

const port = Number(process.env.PORT ?? 8080);

const server = http.createServer((req, res) => {
  if (req.url === "/health") {
    res.writeHead(200, { "content-type": "application/json" });
    res.end(JSON.stringify({ status: "ok" }));
    return;
  }

  res.writeHead(404, { "content-type": "application/json" });
  res.end(JSON.stringify({ error: "not_found" }));
});

const wss = new WebSocketServer({ server, path: "/ws" });

wss.on("connection", (ws, req) => {
  ws.send(
    JSON.stringify({
      type: "welcome",
      remote: req.socket.remoteAddress,
    }),
  );

  ws.on("message", (data) => {
    ws.send(data);
  });
});

server.listen(port, "0.0.0.0", () => {
  // eslint-disable-next-line no-console
  console.log(`ws-server listening on :${port}`);
});
