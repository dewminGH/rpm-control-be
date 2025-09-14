import { Client, neonConfig } from "@neondatabase/serverless";
import ws from "ws";
import type { Server } from "socket.io";
import { DBConnection } from "./db";

neonConfig.webSocketConstructor = ws;

export function startFanRpmListener(io: Server) {
  let stopped = false;
  let client: Client | null = null;
  let keepAlive: NodeJS.Timeout | null = null;

  io.on("connection", (socket) => {
    const deviceSecret =
      socket.handshake.auth.device_secret ||
      socket.handshake.query.device_secret;

    if (deviceSecret) {
      socket.join(`device:${deviceSecret}`);
      console.log(`Client joined room device:${deviceSecret}`);
    } else {
      console.warn("Client connected without device_secret");
    }
  });

  (async function loop() {
    while (!stopped) {
      try {
        const cs = process.env.DATABASE_URL!;
        client = new Client({ connectionString: cs });
        await client.connect();
        await client.query("LISTEN fan_rpm_channel");

        keepAlive = setInterval(
          () => client!.query("SELECT 1").catch(() => {}),
          60_000
        );

        client.on("notification", async (msg: any) => {
          if (msg.channel !== "fan_rpm_channel") return;

          let latest: any = null;
          try {
            latest = JSON.parse(msg.payload ?? "{}");
          } catch (err) {
            console.error("Failed to parse payload:", err);
            return;
          }

          if (!latest?.device_secret) {
            console.warn("Notification missing device_secret:", latest);
            return;
          }

          let lastTenRecords: any[] = [];
          try {
            lastTenRecords = await DBConnection`
              SELECT *
              FROM fan_rpms
              WHERE device_secret = ${latest.device_secret}
              ORDER BY id DESC
              LIMIT 20
            `;
          } catch (_) {
            console.log(_);
          }

          console.log({ latest });

          io.to(`device:${latest.device_secret}`).emit("rpm-sync", {
            latest,
            lastTenRecords,
          });
        });

        await new Promise<void>((resolve) => {
          const done = () => resolve();
          client!.once("end", done);
          client!.once("error", done);
        });
      } catch (e) {
        console.error("[DB] listener error:", e);
      } finally {
        if (keepAlive) {
          clearInterval(keepAlive);
          keepAlive = null;
        }
        try {
          await client?.end();
        } catch {}
        client = null;
      }
      if (!stopped) await new Promise((r) => setTimeout(r, 2000));
    }
  })();

  return {
    stop: async () => {
      stopped = true;
      if (keepAlive) {
        clearInterval(keepAlive);
        keepAlive = null;
      }
      try {
        await client?.end();
      } catch {}
    },
  };
}
