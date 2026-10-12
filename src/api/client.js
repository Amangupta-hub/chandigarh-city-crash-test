
const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

async function request(path, options = {}) {
    const response = await fetch(`${API_BASE_URL}${path}`, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...options.headers,
        },
    });

    if (!response.ok) {
        const detail = await response.text();
        throw new Error(`API error ${response.status}: ${detail}`);
    }

    return response.json();
}

export function getSectors() {
    return request("/api/sectors");
}

export function getEvents(sectorId) {
    const query = sectorId
        ? `?sector_id=${encodeURIComponent(sectorId)}`
        : "";

    return request(`/api/events${query}`);
}

export function runStressTest(scenario) {
    return request("/api/stress-test", {
        method: "POST",
        body: JSON.stringify(scenario),
    });
}

export function optimizeInterventions(scenario) {
    return request("/api/optimize", {
        method: "POST",
        body: JSON.stringify(scenario),
    });
}

export function getScenarios() {
    return request("/api/scenarios");
}

export function saveScenario(scenario) {
    return request("/api/scenarios", {
        method: "POST",
        body: JSON.stringify(scenario),
    });
}
