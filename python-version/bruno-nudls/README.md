
# Nudls API Collection

This directory contains the [Bruno](https://github.com/usebruno/bruno) API collection for testing the Nudls Dinopark backend API.

## Setup

1.  **Install Bruno**: Download and install the [Bruno API Client](https://www.usebruno.com/downloads).
2.  **Open Collection**:
    *   Open Bruno.
    *   Click "Open Collection".
    *   Select this folder (`bruno-nudls`).

## Environment

This collection comes with a pre-configured environment: `dev`.

*   **Select Environment**: In the top right corner of Bruno, select `dev` from the dropdown list.
*   **Variables**:
    *   `baseUrl`: `http://localhost:8000` (Default local API URL)
    *   `dinoId`: `1039` (Sample dinosaur ID for testing details)

## Requests

The collection includes the following requests:
1.  **Get Park Grid**: Retrieves the status of the entire park grid (Safety and Maintenance).
    *   `GET /park/grid`
2.  **Get All Dinosaurs**: Lists all dinosaurs strictly from the database.
    *   `GET /park/dinosaurs`
3.  **Get Dinosaur Details**: Fetches specific details for a dinosaur by ID.
    *   `GET /park/dinosaurs/{{dinoId}}`
