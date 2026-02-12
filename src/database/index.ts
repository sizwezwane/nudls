import sqlite3 from 'sqlite3';
import { open, Database } from 'sqlite';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export let db: Database;

export async function initDb() {
    db = await open({
        filename: path.join(__dirname, '../../dinopark.db'),
        driver: sqlite3.Database
    });

    await db.exec(`
        CREATE TABLE IF NOT EXISTS dinosaurs (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            species TEXT NOT NULL,
            gender TEXT NOT NULL,
            digestion_period_in_hours INTEGER NOT NULL,
            herbivore BOOLEAN NOT NULL,
            location TEXT NOT NULL,
            last_fed_time TEXT
        );

        CREATE TABLE IF NOT EXISTS maintenance_logs (
            location TEXT PRIMARY KEY,
            last_maintenance_time TEXT NOT NULL
        );
    `);
}
