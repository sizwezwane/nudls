import express from 'express';
import { initDb } from './database/index.js';
import { startCron, fetchAndProcessFeed } from './services/nudlsConsumer.js';
import parkRouter from './routers/park.js';

const app = express();
const port = 8000;

app.use(express.json());

app.get('/', (req, res) => {
    res.json({ message: "Welcome to Dinopark Maintenance API" });
});

app.use('/park', parkRouter);

async function startServer() {
    await initDb();
    console.log("Database initialized.");

    // Fetch once on startup then start cron
    if (process.env.NODE_ENV !== 'test') {
        fetchAndProcessFeed();
        startCron();
    }

    if (process.env.NODE_ENV !== 'test') {
        app.listen(port, () => {
            console.log(`API listening at http://localhost:${port}`);
        });
    }
}

if (process.env.NODE_ENV !== 'test') {
    startServer();
}

export { app, startServer };
