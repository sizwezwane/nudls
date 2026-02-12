import { Router } from 'express';
import { getAllDinosaurs, getMaintenanceLogs } from '../crud/index.js';
import { ZoneStatus } from '../schemas/zod.js';

const router = Router();

router.get('/grid', async (req, res) => {
    const dinos = await getAllDinosaurs();
    const maintenanceLogs = await getMaintenanceLogs();
    const now = new Date();

    const grid: ZoneStatus[][] = [];
    const rows = 16;
    const cols = 26;

    for (let r = 0; r < rows; r++) {
        const rowData: ZoneStatus[] = [];
        for (let c = 0; c < cols; c++) {
            const letter = String.fromCharCode(65 + c);
            const zoneId = `${letter}${r}`;

            const zoneDinos = dinos.filter(d => d.location === zoneId);

            let isSafe = true;
            for (const dino of zoneDinos) {
                if (dino.herbivore) continue;

                if (!dino.last_fed_time) {
                    isSafe = false;
                    break;
                }

                const lastFed = new Date(dino.last_fed_time);
                const diffHours = (now.getTime() - lastFed.getTime()) / (1000 * 60 * 60);
                if (diffHours >= dino.digestion_period_in_hours) {
                    isSafe = false;
                    break;
                }
            }

            let maintenanceRequired = true;
            const lastMaintenance = maintenanceLogs[zoneId];
            if (lastMaintenance) {
                const diffDays = (now.getTime() - lastMaintenance.getTime()) / (1000 * 60 * 60 * 24);
                if (diffDays <= 30) {
                    maintenanceRequired = false;
                }
            }

            rowData.push({
                id: zoneId,
                is_safe: isSafe,
                maintenance_required: maintenanceRequired,
                dinosaurs: zoneDinos.map(d => d.name)
            });
        }
        grid.push(rowData);
    }

    res.json(grid);
});

export default router;
