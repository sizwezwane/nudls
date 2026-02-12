import { db } from '../database/index.js';
import type { Dinosaur } from '../schemas/zod.js';

export async function getAllDinosaurs(): Promise<Dinosaur[]> {
    const dinos = await db.all('SELECT * FROM dinosaurs');
    return dinos.map(d => ({
        ...d,
        herbivore: !!d.herbivore,
    }));
}

export async function getMaintenanceLogs(): Promise<Record<string, Date>> {
    const logs = await db.all('SELECT * FROM maintenance_logs');
    const result: Record<string, Date> = {};
    logs.forEach(log => {
        result[log.location] = new Date(log.last_maintenance_time);
    });
    return result;
}

export async function upsertDinosaur(dino: Dinosaur) {
    await db.run(
        `INSERT INTO dinosaurs (id, name, species, gender, digestion_period_in_hours, herbivore, location, last_fed_time)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?)
     ON CONFLICT(id) DO UPDATE SET
     location=excluded.location,
     last_fed_time=excluded.last_fed_time`,
        [dino.id, dino.name, dino.species, dino.gender, dino.digestion_period_in_hours, dino.herbivore ? 1 : 0, dino.location, dino.last_fed_time]
    );
}

export async function upsertMaintenance(location: string, time: string) {
    await db.run(
        `INSERT INTO maintenance_logs (location, last_maintenance_time)
     VALUES (?, ?)
     ON CONFLICT(location) DO UPDATE SET
     last_maintenance_time=excluded.last_maintenance_time`,
        [location, time]
    );
}
