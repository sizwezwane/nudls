import { z } from 'zod';

export const DinosaurSchema = z.object({
    id: z.number(),
    name: z.string(),
    species: z.string(),
    gender: z.string(),
    digestion_period_in_hours: z.number(),
    herbivore: z.boolean(),
    location: z.string(),
    last_fed_time: z.string().nullable(),
});

export type Dinosaur = z.infer<typeof DinosaurSchema>;

export const ZoneStatusSchema = z.object({
    id: z.string(),
    is_safe: z.boolean(),
    maintenance_required: z.boolean(),
    dinosaurs: z.array(z.string()),
});

export type ZoneStatus = z.infer<typeof ZoneStatusSchema>;
