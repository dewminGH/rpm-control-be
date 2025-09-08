import { DBConnection } from "./db/db";
import { startFanRpmListener } from "./db/rpm-insert-listener";

require("dotenv").config();

const app = require("express")();
const server = require("http").createServer(app);
const { Server } = require("socket.io");
const cors = require("cors");

console.log(DBConnection);
app.use(cors({ origin: ["http://localhost:5173"], credentials: true }));
const io = new Server(server, {
  cors: {
    origin: "http://localhost:5173",
    methods: ["GET", "POST"],
    credentials: true,
  },
});

io.on("connection", async (socket: any) => {
  console.log("socket", socket.id);
  socket.on("msg-sync", (data: any) => {
    console.log("data incoming", data);
    socket.emit("msg-sync", { data: `from server ${data}` });
  });
});

startFanRpmListener(io);

server.listen(3000, () => console.log("running server @ port 3000"));

// io.on("connection", (socket) => {
//   console.log("socket connected:", socket.id);
//   socket.on("message", (data) => {
//     console.log("recv:", data);
//     socket.emit("message", `msg from server ${data}`);
//   });
// });
