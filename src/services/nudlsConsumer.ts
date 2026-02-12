import axios from 'axios';
import cron from 'node-cron';
import { db } from '../database/index.js';

const NUDLS_FEED_URL = "https://dinoparks.herokuapp.com/nudls/feed";

export async function fetchAndProcessFeed() {
    console.log("Starting NUDLS feed fetch...");
    try {
        const response = await axios.get(NUDLS_FEED_URL);
        const events = response.data;

        // Sort events by time ascending to reconstruct state chronologically
        events.sort((a: any, b: any) => new Date(a.time).getTime() - new Date(b.time).getTime());

        for (const event of events) {
            await processEvent(event);
        }
        console.log("Finished processing NUDLS feed.");
    } catch (error) {
        console.error("Failed to fetch NUDLS feed:", error);
    }
}

async function processEvent(event: any) {
    const kind = event.kind;
    const eventTime = new Date(event.time);

    if (kind === 'dino_added') {
        await db.run(
            `INSERT OR IGNORE INTO dinosaurs (id, name, species, gender, digestion_period_in_hours, herbivore, location)
             VALUES (?, ?, ?, ?, ?, ?, ?)`,
            [event.id, event.name, event.species, event.gender, event.digestion_period_in_hours, event.herbivore ? 1 : 0, '']
        );
    } else if (kind === 'dino_removed') {
        await db.run('DELETE FROM dinosaurs WHERE id = ?', [event.dinosaur_id]);
    } else if (kind === 'dino_location_updated') {
        const dino = await db.get('SELECT * FROM dinosaurs WHERE id = ?', [event.dinosaur_id]);
        if (dino) {
            // In a real app we'd track last_location_update_time
            await db.run('UPDATE dinosaurs SET location = ? WHERE id = ?', [event.location, event.dinosaur_id]);
        }
    } else if (kind === 'dino_fed') {
        const dino = await db.get('SELECT * FROM dinosaurs WHERE id = ?', [event.dinosaur_id]);
        if (dino && (!dino.last_fed_time || eventTime > new Date(dino.last_fed_time))) {
            await db.run('UPDATE dinosaurs SET last_fed_time = ? WHERE id = ?', [event.time, event.dinosaur_id]);
        }
    } else if (kind === 'maintenance_performed') {
        const log = await db.get('SELECT * FROM maintenance_logs WHERE location = ?', [event.location]);
        if (!log || eventTime > new Date(log.last_maintenance_time)) {
            await db.run(
                'INSERT INTO maintenance_logs (location, last_maintenance_time) VALUES (?, ?) ON CONFLICT(location) DO UPDATE SET last_maintenance_time = excluded.last_maintenance_time',
                [event.location, event.time]
            );
        }
    }
}

export function startCron() {
    cron.schedule('* * * * *', () => {
        fetchAndProcessFeed();
    });
}
