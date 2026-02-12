import request from 'supertest';
import { app, startServer } from '../src/index';
import { db } from '../src/database/index';

beforeAll(async () => {
    process.env.NODE_ENV = 'test';
    await startServer();
});

describe('API Endpoints', () => {
    it('should return welcome message', async () => {
        const res = await request(app).get('/');
        expect(res.status).toBe(200);
        expect(res.body.message).toBe('Welcome to Dinopark Maintenance API');
    });

    it('should return the park grid', async () => {
        const res = await request(app).get('/park/grid');
        expect(res.status).toBe(200);
        expect(Array.isArray(res.body)).toBe(true);
        expect(res.body.length).toBe(16);
        expect(res.body[0].length).toBe(26);
    });
});

describe('Safety Logic', () => {
    it('should identify unsafe zones with hungry carnivores', async () => {
        // Clear and setup test data
        await db.run('DELETE FROM dinosaurs');
        const now = new Date().toISOString();
        const longAgo = new Date(Date.now() - 100 * 60 * 60 * 1000).toISOString(); // 100h ago

        // Herbivore -> Safe
        await db.run(
            `INSERT INTO dinosaurs (id, name, species, gender, digestion_period_in_hours, herbivore, location)
           VALUES (?, ?, ?, ?, ?, ?, ?)`,
            [1, 'Herbie', 'Stego', 'M', 4, 1, 'A0']
        );

        // Carnivore, hungry -> Unsafe
        await db.run(
            `INSERT INTO dinosaurs (id, name, species, gender, digestion_period_in_hours, herbivore, location)
           VALUES (?, ?, ?, ?, ?, ?, ?)`,
            [2, 'Rex', 'TRex', 'M', 48, 0, 'B0']
        );

        // Carnivore, fed recently -> Safe
        await db.run(
            `INSERT INTO dinosaurs (id, name, species, gender, digestion_period_in_hours, herbivore, location, last_fed_time)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
            [3, 'RexJunior', 'TRex', 'M', 48, 0, 'C0', now]
        );

        // Carnivore, fed long ago -> Unsafe
        await db.run(
            `INSERT INTO dinosaurs (id, name, species, gender, digestion_period_in_hours, herbivore, location, last_fed_time)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
            [4, 'RexSenior', 'TRex', 'M', 48, 0, 'D0', longAgo]
        );

        const res = await request(app).get('/park/grid');
        const grid = res.body;

        // A0 (index 0,0) -> Safe
        expect(grid[0][0].is_safe).toBe(true);
        // B0 (index 0,1) -> Unsafe
        expect(grid[0][1].is_safe).toBe(false);
        // C0 (index 0,2) -> Safe
        expect(grid[0][2].is_safe).toBe(true);
        // D0 (index 0,3) -> Unsafe
        expect(grid[0][3].is_safe).toBe(false);
    });
});
