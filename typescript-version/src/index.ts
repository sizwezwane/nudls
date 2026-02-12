import express from 'express';
import { initDb } from './database/index.js';
import { startCron, fetchAndProcessFeed } from './services/nudlsConsumer.js';
import parkRouter from './routers/park.js';

const app = express();
const port = 8001;

app.use(express.json());

app.get('/', (req, res) => {
    res.json({ message: "Welcome to Dinopark Maintenance API (TypeScript Version)" });
});

app.use('/park', parkRouter);

async function start() {
    await initDb();
    console.log("Database initialized.");

    // Fetch once on startup then start cron
    fetchAndProcessFeed();
    startCron();

    app.listen(port, () => {
        console.log(`TypeScript API listening at http://localhost:${port}`);
    });
}

start();
