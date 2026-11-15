const API_URL = "http://localhost:8000";

export async function checkBackend() {
	const response = await fetch(`${API_URL}/health`, {
		cache: "no-store",
	});

	if (!response.ok) {
		throw new Error("Backend connection failed");
	}

	return response.json();
}

export async function getDashboardOverview() {
	const response = await fetch(`${API_URL}/dashboard/overview`, {
		cache: "no-store",
	});

	if (!response.ok) {
		throw new Error("Unable to fetch dashboard data");
	}

	return response.json();
}